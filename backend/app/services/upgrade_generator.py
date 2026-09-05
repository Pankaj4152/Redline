import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)
from app.models.schemas import (
    RepoContextSummary,
    TaskImpactResult,
    SimulationProfileResult,
    SignalHealthReport,
    TaskRecommendation
)
from app.services.context_budgeter import context_budget_service

SYSTEM_UPGRADE_PROMPT = """
You are an expert Coding Assessment Task Red-Teamer & Design Specialist.
Your job is to take a weak or delegable coding assessment task description and upgrade it into a high-signal task.

Rules:
1. Do NOT add massive new feature scopes that double the task duration.
2. Inject non-obvious architectural constraints (e.g. streaming RAM limits, error contracts, middleware reuse).
3. Output a JSON object adhering strictly to the TaskRecommendation schema.
""".strip()


class UpgradeGeneratorService:
    """
    Service responsible for generating actionable, repository-specific task upgrades
    that elevate engineering signal without inflating task completion time.
    """

    def generate_mock_upgrade(
        self,
        summary: RepoContextSummary,
        impact: TaskImpactResult,
        simulations: list[SimulationProfileResult],
        report: SignalHealthReport,
        task_description: str
    ) -> TaskRecommendation:
        """
        Generates a repository-specific heuristic task upgrade for mock / dev / test execution.
        """
        is_weak_signal = report.overall_health_score < 65
        
        # Extract grounding chain from task impact
        grounding = impact.grounding_chain if impact.grounding_chain else None

        if is_weak_signal:
            upgraded = (
                f"{task_description.strip()} Implement the search feature using the repository's existing "
                f"pagination and query filter conventions. Handle empty queries, zero search matches, and requests "
                f"exceeding available result sets. Include automated unit tests covering these edge cases."
            )
            rationale = (
                "Forces the candidate to inspect existing repository route & model patterns rather than copying a generic "
                "AI snippet. Grounded strictly in detected codebase abstractions without introducing unsupported constraints."
            )
            constraints = [
                "Reuse existing repository pagination & query filter conventions",
                "Handle boundary cases (empty query, no matches, out-of-bound page requests)",
                "Add automated unit tests covering boundary failure modes"
            ]
        else:
            upgraded = (
                f"{task_description.strip()} Include automated unit tests covering non-obvious failure modes "
                f"and verify edge-case exception handling contracts."
            )
            rationale = (
                "The task already demands architectural judgment. Adding explicit boundary verification "
                "prevents candidates from submitting happy-path implementations."
            )
            constraints = [
                "Add unit tests for non-obvious boundary failure modes",
                "Verify edge-case exception handling contracts"
            ]

        return TaskRecommendation(
            original_task=task_description.strip(),
            upgraded_task=upgraded,
            rationale=rationale,
            added_constraints=constraints,
            grounding_chain=grounding
        )

    def generate_task_upgrade(
        self,
        summary: RepoContextSummary,
        impact: TaskImpactResult,
        simulations: list[SimulationProfileResult],
        report: SignalHealthReport,
        task_description: str
    ) -> TaskRecommendation:
        """
        Generates an upgraded task description using Gemini LLM (or mock fallback).
        """
        if settings.USE_MOCK_LLM or not settings.GEMINI_API_KEY:
            return self.generate_mock_upgrade(summary, impact, simulations, report, task_description)

        prompt_data = context_budget_service.build_analysis_prompt_context(summary, task_description)
        user_prompt = f"""
{prompt_data['security_framed_repo_data']}

HEALTH REPORT VERDICT: {report.verdict} (Overall Score: {report.overall_health_score})
AI SOLVABILITY: {report.ai_solvability.score}% ({', '.join(report.ai_solvability.contributing_evidence)})

ORIGINAL TASK DESCRIPTION:
{prompt_data['candidate_task_description']}

Formulate an upgraded task description with rationale and return the TaskRecommendation JSON.
"""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_UPGRADE_PROMPT,
                    response_mime_type="application/json",
                    response_schema=TaskRecommendation,
                    temperature=0.2
                )
            )
            data = json.loads(response.text)
            return TaskRecommendation.model_validate(data)
        except Exception as e:
            logger.exception("Gemini API call failed in UpgradeGeneratorService; returning heuristic mock upgrade recommendation.")
            return self.generate_mock_upgrade(summary, impact, simulations, report, task_description)


upgrade_generator_service = UpgradeGeneratorService()
