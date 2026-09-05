import uuid
from app.core.config import settings
from app.models.schemas import AnalysisRequest, FullAssessmentResult
from app.services.repo_analyzer import repo_analyzer_service
from app.services.task_impact import task_impact_service
from app.services.strategy_simulator import strategy_simulator_service
from app.services.signal_evaluator import signal_evaluation_service
from app.services.upgrade_generator import upgrade_generator_service


class AnalysisOrchestratorService:
    """
    Master Pipe-and-Filter Orchestrator Service chaining all analytical components:
    RepoAnalyzer -> ContextBudgeter -> TaskImpact -> StrategySimulator -> SignalEvaluator -> UpgradeGenerator.
    """

    def run_analysis_pipeline(self, request: AnalysisRequest) -> FullAssessmentResult:
        """
        Executes the end-to-end Redline evaluation pipeline for a given AnalysisRequest.
        """
        job_id = f"job_{uuid.uuid4().hex[:10]}"

        # Step 1: Secure Repository Ingestion & Static AST Symbol Extraction
        repo_summary = repo_analyzer_service.analyze_repository(
            repo_url=request.repo_url,
            branch=request.branch,
            cleanup=True
        )

        # Step 2: Assessment Task Impact Mapping (Blast Radius & touched modules)
        task_impact = task_impact_service.analyze_task_impact(
            summary=repo_summary,
            task_description=request.task_description
        )

        # Step 3: Candidate Strategy Simulation across 3 profiles
        simulations = strategy_simulator_service.simulate_strategies(
            summary=repo_summary,
            impact=task_impact,
            task_description=request.task_description
        )

        # Step 4: Diagnostic Signal Health Scoring & Evidence Linkage
        signal_report = signal_evaluation_service.evaluate_signal_health(
            summary=repo_summary,
            impact=task_impact,
            simulations=simulations,
            task_description=request.task_description
        )

        # Step 5: Recommendation & Task Upgrade Generation
        recommendation = upgrade_generator_service.generate_task_upgrade(
            summary=repo_summary,
            impact=task_impact,
            simulations=simulations,
            report=signal_report,
            task_description=request.task_description
        )

        # Check for artificial complexity warning in report verdict
        is_artificially_complex = "Artificial Complexity" in signal_report.verdict
        complexity_reason = signal_report.reasoning_signal.contributing_evidence[0] if is_artificially_complex else None

        # Check if fallback/mock engine was used
        is_fallback = settings.USE_MOCK_LLM or "Fallback due to API error" in task_impact.summary
        fallback_reason = "Executed with mock heuristics (USE_MOCK_LLM=True or upstream API error)" if is_fallback else None

        # Assemble & Return Complete Result Data Model
        return FullAssessmentResult(
            job_id=job_id,
            status="completed",
            repo_summary=repo_summary,
            report=signal_report,
            simulations=simulations,
            recommendations=recommendation,
            evidence_grounding=task_impact.grounding_chain,
            artificial_complexity_flag=is_artificially_complex,
            complexity_rationale=complexity_reason,
            is_fallback=is_fallback,
            fallback_reason=fallback_reason
        )


orchestrator_service = AnalysisOrchestratorService()
