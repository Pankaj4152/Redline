import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)
from app.models.schemas import (
    RepoContextSummary,
    TaskImpactResult,
    CandidateProfileEnum,
    LevelEnum,
    SimulationProfileResult
)
from app.services.context_budgeter import context_budget_service

SYSTEM_SIMULATION_PROMPT = """
You are an expert AI Strategy Simulator for Software Engineering Assessments.
Your job is to simulate how 3 distinct candidate engineering profiles would solve a candidate task given a repository context outline.

The 3 Profiles:
1. AI-Dependent Engineer: Broad delegation, zero context verification, happy-path reliance.
2. Naive AI-Assisted Engineer: Partial context inspection, happy-path testing, misses non-obvious failure modes.
3. Strong AI-Native Engineer: Deep architectural context inspection, targeted AI prompts, rigorous edge-case verification.

Output Format:
Return a JSON array of 3 objects adhering strictly to the SimulationProfileResult schema.
""".strip()


class StrategySimulatorService:
    """
    Service responsible for simulating AI-assisted candidate profile strategies.
    """

    def generate_mock_simulations(
        self,
        summary: RepoContextSummary,
        impact: TaskImpactResult,
        task_description: str
    ) -> list[SimulationProfileResult]:
        """
        Generates realistic heuristic candidate simulations for mock / dev / test execution.
        """
        touched = impact.impacted_files or summary.file_tree[:2]
        is_high_depth = impact.architectural_depth_required == LevelEnum.HIGH

        # Profile 1: AI-Dependent Engineer
        ai_dependent = SimulationProfileResult(
            profile=CandidateProfileEnum.AI_DEPENDENT,
            success_likelihood=LevelEnum.MEDIUM if is_high_depth else LevelEnum.HIGH,
            estimated_delegation="90%",
            reasoning_summary="Delegates entire task to raw LLM prompt. Copies generated snippet without inspecting existing repo models or conventions.",
            missed_risks=impact.potential_side_effects or ["Ignores existing pagination contracts", "Bypasses error response formats"],
            inspected_files=touched[:1],
            abstractions_reused=[],
            edge_cases_tested=["None (relies purely on default AI output)"]
        )

        # Profile 2: Naive AI-Assisted Engineer
        naive_assisted = SimulationProfileResult(
            profile=CandidateProfileEnum.NAIVE_AI_ASSISTED,
            success_likelihood=LevelEnum.HIGH,
            estimated_delegation="70%",
            reasoning_summary="Uses AI for speed, checks happy-path HTTP 200 response, but misses non-obvious boundary failure modes.",
            missed_risks=["Misses boundary-case handling for empty/invalid parameters"],
            inspected_files=touched[:2],
            abstractions_reused=["HTTP Route Handler"],
            edge_cases_tested=["Happy-path HTTP 200 OK"]
        )

        # Profile 3: Strong AI-Native Engineer
        strong_native = SimulationProfileResult(
            profile=CandidateProfileEnum.STRONG_AI_NATIVE,
            success_likelihood=LevelEnum.HIGH,
            estimated_delegation="40%",
            reasoning_summary="Inspects route + model + CRUD layers, reuses existing repository conventions, and explicitly writes edge-case tests.",
            missed_risks=["Potential minor performance overhead under heavy concurrency"],
            inspected_files=touched,
            abstractions_reused=["Pydantic Schemas", "Existing Pagination Conventions", "Repository CRUD Abstraction"],
            edge_cases_tested=["Empty query string", "No matching search results", "Requests exceeding total result set"]
        )

        return [ai_dependent, naive_assisted, strong_native]

    def simulate_strategies(
        self,
        summary: RepoContextSummary,
        impact: TaskImpactResult,
        task_description: str
    ) -> list[SimulationProfileResult]:
        """
        Runs strategy simulations for the 3 candidate profiles using Gemini LLM (or mock fallback).
        """
        if settings.USE_MOCK_LLM or not settings.GEMINI_API_KEY:
            return self.generate_mock_simulations(summary, impact, task_description)

        prompt_data = context_budget_service.build_analysis_prompt_context(summary, task_description)
        user_prompt = f"""
{prompt_data['security_framed_repo_data']}

TASK IMPACT ANALYSIS:
Architectural Depth: {impact.architectural_depth_required.value}
Impacted Files: {impact.impacted_files}
Potential Side Effects: {impact.potential_side_effects}

CANDIDATE TASK DESCRIPTION:
{prompt_data['candidate_task_description']}

Simulate the 3 candidate profiles and return a JSON list of 3 SimulationProfileResult objects.
"""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_SIMULATION_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            data = json.loads(response.text)
            if isinstance(data, list):
                return [SimulationProfileResult.model_validate(item) for item in data]
            elif isinstance(data, dict) and "simulations" in data:
                return [SimulationProfileResult.model_validate(item) for item in data["simulations"]]
            return self.generate_mock_simulations(summary, impact, task_description)
        except Exception as e:
            logger.exception("Gemini API call failed in StrategySimulatorService; returning heuristic mock simulations.")
            return self.generate_mock_simulations(summary, impact, task_description)


strategy_simulator_service = StrategySimulatorService()
