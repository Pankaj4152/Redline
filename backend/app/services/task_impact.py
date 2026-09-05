import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)
from app.models.schemas import RepoContextSummary, TaskImpactResult, LevelEnum, EvidenceGroundingChain
from app.services.context_budgeter import context_budget_service

SYSTEM_IMPACT_PROMPT = """
You are an expert Software Architecture & Red-Teaming AI Assessor.
Your task is to analyze a proposed candidate coding assessment task against a repository outline and Fact Matrix.

Target Analysis Goal:
Determine which files in the repository will be touched by the task, existing code conventions required, and allowed vs forbidden upgrades strictly grounded in the Fact Matrix.
Do NOT recommend any abstractions listed in absent_abstractions.

Output Format:
Return a JSON object adhering strictly to the TaskImpactResult schema.
""".strip()


class TaskImpactService:
    """
    Service responsible for evaluating candidate assessment tasks against repository context
    to determine touched modules, architectural depth, and potential side effects.
    """

    def generate_mock_impact(self, summary: RepoContextSummary, task_description: str) -> TaskImpactResult:
        """
        Generates a realistic, repository-specific heuristic impact result for mock / dev / test execution.
        """
        task_lower = task_description.lower()
        
        # 1. Identify touched files from repo summary
        impacted_files = [f for f in summary.file_tree if any(k in f.lower() for k in ["api", "route", "service", "handler", "main"])]
        if not impacted_files and summary.file_tree:
            impacted_files = summary.file_tree[:2]
            
        # 2. Identify touched modules
        impacted_modules = list({f.split("/")[0] for f in impacted_files if "/" in f})
        if not impacted_modules:
            impacted_modules = ["core"]

        # 3. Determine architectural depth required
        high_depth_keywords = ["stream", "memory", "thread", "concurrency", "architecture", "middleware", "auth", "cache", "async"]
        if any(kw in task_lower for kw in high_depth_keywords):
            depth = LevelEnum.HIGH
            cross_deps = ["Background Processing Queue", "Memory Management Stream", "Authentication Middleware"]
            side_effects = ["Unbounded RAM usage on large datasets", "Bypassing existing rate-limiters"]
        elif "test" in task_lower or "fix" in task_lower:
            depth = LevelEnum.MEDIUM
            cross_deps = ["Module Unit Test Runner"]
            side_effects = ["Uncaught edge-case exceptions"]
        else:
            depth = LevelEnum.LOW
            cross_deps = ["HTTP Route Handler"]
            side_effects = ["Modifies localized route handler without touching database or abstractions"]

        obs = summary.fact_matrix.observed_abstractions if summary.fact_matrix else ["HTTP Endpoint Routing", "Pydantic Schemas"]
        absent = summary.fact_matrix.absent_abstractions if summary.fact_matrix else ["NO Response Data Streaming", "NO API Rate-Limiting Middleware"]

        grounding_chain = EvidenceGroundingChain(
            repo_facts=obs,
            task_implications=[
                f"Candidate must understand existing route structure ({', '.join(impacted_files[:2]) or 'main.py'})",
                "Task evaluation is constrained to observed repository abstractions"
            ],
            allowed_upgrades=[
                "Require pagination and query filter consistency with existing endpoints",
                "Add boundary-case tests covering empty result sets and invalid parameters"
            ],
            forbidden_upgrades=[
                f"Do NOT recommend: {', '.join(absent[:2])} (Neither abstraction exists in repository)"
            ],
            confidence_rating="High"
        )

        return TaskImpactResult(
            impacted_files=impacted_files[:5],
            impacted_modules=impacted_modules,
            architectural_depth_required=depth,
            cross_module_dependencies=cross_deps,
            potential_side_effects=side_effects,
            summary=f"Task touches {len(impacted_files)} file(s) across modules {impacted_modules}. Requires {depth.value} architectural depth.",
            grounding_chain=grounding_chain
        )

    def analyze_task_impact(self, summary: RepoContextSummary, task_description: str) -> TaskImpactResult:
        """
        Analyzes the candidate task against the repository context using Gemini LLM (or mock fallback).
        """
        # If mock mode is enabled or API key is absent, use heuristic mock impact generator
        if settings.USE_MOCK_LLM or not settings.GEMINI_API_KEY:
            return self.generate_mock_impact(summary, task_description)

        # Live Gemini API execution
        prompt_data = context_budget_service.build_analysis_prompt_context(summary, task_description)
        user_prompt = f"""
{prompt_data['security_framed_repo_data']}

CANDIDATE TASK DESCRIPTION TO EVALUATE:
{prompt_data['candidate_task_description']}

Map the task against the repository data above and return the TaskImpactResult JSON.
"""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_IMPACT_PROMPT,
                    response_mime_type="application/json",
                    response_schema=TaskImpactResult,
                    temperature=0.2
                )
            )
            
            # Parse structured JSON output
            data = json.loads(response.text)
            return TaskImpactResult.model_validate(data)

        except Exception as e:
            logger.exception("Gemini API call failed in TaskImpactService; returning heuristic mock fallback.")
            mock_result = self.generate_mock_impact(summary, task_description)
            mock_result.summary += f" (Fallback due to API error: {str(e)})"
            return mock_result


task_impact_service = TaskImpactService()
