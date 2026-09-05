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
        
        # 1. AI Solvability Metric (High score = easily solvable by raw AI)
        if not is_high_depth:
            ai_solvability_score = 85
            ai_solvability_level = LevelEnum.HIGH
            ai_solvability_evidence = [
                "Default AI prompt generates a working solution on first try without inspecting repository abstractions.",
                f"Modifies localized file(s) ({', '.join(impact.impacted_files[:2])}) without touching existing middleware."
            ]
        else:
            ai_solvability_score = 35
            ai_solvability_level = LevelEnum.LOW
            ai_solvability_evidence = [
                "Raw AI prompts generate generic snippets that fail to handle memory constraints.",
                "Requires non-obvious interface integration across modules."
            ]

        # 2. Reasoning Signal Metric
        reasoning_score = 75 if is_high_depth else 30
        reasoning_level = LevelEnum.HIGH if is_high_depth else LevelEnum.LOW
        reasoning_evidence = [
            "Demands explicit memory streaming constraints and error contract verification." if is_high_depth
            else "Task requires minimal cross-module reasoning or failure mode validation."
        ]

        # 3. Repo Depth Metric
        repo_depth_score = 70 if len(impact.impacted_files) > 1 else 25
        repo_depth_level = LevelEnum.HIGH if len(impact.impacted_files) > 1 else LevelEnum.LOW
        repo_depth_evidence = [
            f"Touches {len(impact.impacted_files)} file(s) across module boundaries ({', '.join(impact.impacted_modules)})." if len(impact.impacted_files) > 1
            else "Requires zero interaction with underlying database connections or background worker queues."
        ]

        # 4. Architectural Judgment Metric
        arch_score = 80 if is_high_depth else 20
        arch_level = LevelEnum.HIGH if is_high_depth else LevelEnum.LOW
        arch_evidence = [
            "Candidate must balance memory limits against response throughput." if is_high_depth
            else "Standard boilerplate pattern can be pasted without evaluating system trade-offs."
        ]

        # 5. Verification Requirement Metric
        verif_score = 75 if is_high_depth else 35
        verif_level = LevelEnum.HIGH if is_high_depth else LevelEnum.LOW
        verif_evidence = [
            "Requires stress testing non-obvious failure modes under high volume data." if is_high_depth
            else "Superficial happy-path HTTP 200 check passes without validating edge cases."
        ]

        # Overall Health Score (Weighted calculation: higher = stronger signal)
        overall_health = int(
            (100 - ai_solvability_score) * 0.30 +
            reasoning_score * 0.25 +
            repo_depth_score * 0.15 +
            arch_score * 0.15 +
            verif_score * 0.15
        )

        verdict = (
            "Strong Signal - High Architectural Judgment Demanded" if overall_health >= 65
            else "Moderate Signal - Partial AI Delegation Risk" if overall_health >= 45
            else "Weak Signal - Highly AI-Delegable"
        )

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
            logger.exception("Gemini API call failed in SignalEvaluationService; returning heuristic mock evaluation.")
            return self.generate_mock_evaluation(summary, impact, simulations, task_description)


signal_evaluation_service = SignalEvaluationService()
