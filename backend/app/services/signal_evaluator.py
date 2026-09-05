import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)
from app.models.schemas import (
    RepoContextSummary,
    TaskImpactResult,
    SimulationProfileResult,
    MetricScore,
    SignalHealthReport,
    LevelEnum,
    CandidateProfileEnum
)
from app.services.context_budgeter import context_budget_service

SYSTEM_EVALUATOR_PROMPT = """
You are an expert Engineering Assessment Health Evaluator.
Evaluate a coding task across 5 dimensions: AI Solvability, Reasoning Signal, Repo Depth, Architectural Judgment, Verification Requirement.

Rule: Every single dimension score MUST include mandatory qualitative contributing evidence strings.
Output Format: Return a JSON object adhering strictly to the SignalHealthReport schema.
""".strip()


class SignalEvaluationService:
    """
    Service responsible for calculating heuristic assessment signal health scores
    and linking transparent qualitative evidence to each evaluated metric.
    """

    def generate_mock_evaluation(
        self,
        summary: RepoContextSummary,
        impact: TaskImpactResult,
        simulations: list[SimulationProfileResult],
        task_description: str
    ) -> SignalHealthReport:
        """
        Generates a transparent heuristic signal health report for mock / dev / test execution.
        """
        is_high_depth = impact.architectural_depth_required == LevelEnum.HIGH
        
        file_count = len(impact.impacted_files)
        module_count = len(impact.impacted_modules)
        task_len = len(task_description.strip())
        
        # 1. AI Solvability Metric (High score = easily solvable by raw AI)
        if not is_high_depth:
            ai_solvability_score = max(55, 90 - (file_count * 5))
            ai_solvability_level = LevelEnum.HIGH
            ai_solvability_evidence = [
                "Default AI prompt generates a working solution on first try without inspecting repository abstractions.",
                f"Modifies localized file(s) ({', '.join(impact.impacted_files[:2]) or 'main.py'}) without touching existing middleware."
            ]
        else:
            ai_solvability_score = max(20, 45 - (file_count * 5))
            ai_solvability_level = LevelEnum.LOW
            ai_solvability_evidence = [
                "Raw AI prompts generate generic snippets that fail to handle boundary constraints.",
                "Requires non-obvious interface integration across modules."
            ]

        # 2. Reasoning Signal Metric
        reasoning_score = min(95, (60 if is_high_depth else 30) + min(25, task_len // 20))
        reasoning_level = LevelEnum.HIGH if reasoning_score >= 65 else LevelEnum.MEDIUM if reasoning_score >= 45 else LevelEnum.LOW
        reasoning_evidence = [
            "Demands repository-grounded constraints and error contract verification." if is_high_depth
            else "Task requires minimal cross-module reasoning or failure mode validation."
        ]

        # 3. Repo Depth Metric
        repo_depth_score = min(95, 20 + (file_count * 15) + (module_count * 10))
        repo_depth_level = LevelEnum.HIGH if repo_depth_score >= 65 else LevelEnum.MEDIUM if repo_depth_score >= 45 else LevelEnum.LOW
        repo_depth_evidence = [
            f"Touches {file_count} file(s) across module boundaries ({', '.join(impact.impacted_modules)})." if file_count > 1
            else "Requires minimal interaction with underlying repository abstractions."
        ]

        # 4. Architectural Judgment Metric
        arch_score = min(95, (65 if is_high_depth else 25) + (module_count * 10))
        arch_level = LevelEnum.HIGH if arch_score >= 65 else LevelEnum.MEDIUM if arch_score >= 45 else LevelEnum.LOW
        arch_evidence = [
            "Candidate must balance model constraints against API interface contracts." if is_high_depth
            else "Standard boilerplate pattern can be pasted without evaluating system trade-offs."
        ]

        # 5. Verification Requirement Metric
        verif_score = min(95, (65 if is_high_depth else 30) + ("test" in task_description.lower()) * 20)
        verif_level = LevelEnum.HIGH if verif_score >= 65 else LevelEnum.MEDIUM if verif_score >= 45 else LevelEnum.LOW
        verif_evidence = [
            "Requires stress testing non-obvious boundary failure modes." if verif_score >= 60
            else "Superficial happy-path HTTP 200 check passes without validating edge cases."
        ]

        # Calculate Dynamic Overall Health Score (Weighted Formula)
        overall_health = int(
            (100 - ai_solvability_score) * 0.30 +
            reasoning_score * 0.25 +
            repo_depth_score * 0.15 +
            arch_score * 0.15 +
            verif_score * 0.15
        )

        # Check for Artificial Complexity (ungrounded requirements)
        task_clean = task_description.lower().replace("-", " ")
        absent_list = summary.fact_matrix.absent_abstractions if summary.fact_matrix else []
        ungrounded_matches = []
        for a in absent_list:
            clean_fact = a.replace("NO ", "").split("(")[0].strip().lower().replace("-", " ")
            fact_tokens = [t for t in clean_fact.split() if len(t) > 3]
            if any(token in task_clean for token in fact_tokens):
                ungrounded_matches.append(a)

        is_artificially_complex = len(ungrounded_matches) >= 1

        if is_artificially_complex:
            # Apply dynamic penalty to health score for artificial bloat
            overall_health = max(15, overall_health - 25)
            verdict = "Artificial Complexity Warning - Ungrounded Architectural Bloat"
            reasoning_evidence = [
                f"Task introduces ungrounded constraints not supported by repo: {', '.join(ungrounded_matches)}",
                "High implementation bloat without proportional increase in true engineering signal."
            ]
        elif overall_health >= 65:
            verdict = "Strong Signal - High Engineering Judgment Required"
            reasoning_evidence = [
                "Demands repository-grounded pagination and error contract verification.",
                "Requires candidate to reuse existing repository conventions."
            ]
        elif overall_health >= 45:
            verdict = "Moderate Signal - Moderate Architectural Signal"
            reasoning_evidence = [
                "Task touches multiple files but has localized AI delegation surface area."
            ]
        else:
            verdict = "Weak Signal - Highly AI-Delegable"
            reasoning_evidence = [
                "Task requires minimal cross-module reasoning or failure mode validation."
            ]

        return SignalHealthReport(
            overall_health_score=overall_health,
            verdict=verdict,
            ai_solvability=MetricScore(score=ai_solvability_score, level=ai_solvability_level, contributing_evidence=ai_solvability_evidence),
            reasoning_signal=MetricScore(score=reasoning_score, level=reasoning_level, contributing_evidence=reasoning_evidence),
            repo_depth=MetricScore(score=repo_depth_score, level=repo_depth_level, contributing_evidence=repo_depth_evidence),
            architectural_judgment=MetricScore(score=arch_score, level=arch_level, contributing_evidence=arch_evidence),
            verification_requirement=MetricScore(score=verif_score, level=verif_level, contributing_evidence=verif_evidence)
        )

    def evaluate_signal_health(
        self,
        summary: RepoContextSummary,
        impact: TaskImpactResult,
        simulations: list[SimulationProfileResult],
        task_description: str
    ) -> SignalHealthReport:
        """
        Calculates diagnostic assessment health report using Gemini LLM (or mock fallback).
        """
        self.last_error = None
        if settings.USE_MOCK_LLM or not settings.GEMINI_API_KEY:
            return self.generate_mock_evaluation(summary, impact, simulations, task_description)

        prompt_data = context_budget_service.build_analysis_prompt_context(summary, task_description)
        user_prompt = f"""
{prompt_data['security_framed_repo_data']}

TASK IMPACT:
Architectural Depth: {impact.architectural_depth_required.value}
Impacted Files: {impact.impacted_files}

SIMULATION RESULTS:
{json.dumps([s.model_dump() for s in simulations], indent=2)}

Evaluate the 5 signal dimensions and return the SignalHealthReport JSON object.
"""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_EVALUATOR_PROMPT,
                    response_mime_type="application/json",
                    response_schema=SignalHealthReport,
                    temperature=0.2
                )
            )
            data = json.loads(response.text)
            return SignalHealthReport.model_validate(data)
        except Exception as e:
            err_msg = f"SignalEvaluationService: {str(e)}"
            self.last_error = err_msg
            logger.exception("Gemini API call failed in SignalEvaluationService; returning heuristic mock evaluation.")
            return self.generate_mock_evaluation(summary, impact, simulations, task_description)



signal_evaluation_service = SignalEvaluationService()
