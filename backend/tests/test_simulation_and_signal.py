from app.models.schemas import (
    RepoContextSummary,
    RepoSymbol,
    LevelEnum,
    CandidateProfileEnum,
    SignalHealthReport,
    SimulationProfileResult
)
from app.services.task_impact import task_impact_service
from app.services.strategy_simulator import strategy_simulator_service
from app.services.signal_evaluator import signal_evaluation_service

def test_strategy_simulator_three_profiles():
    summary = RepoContextSummary(
        repo_name="sample-app",
        total_files=3,
        file_tree=["app/main.py", "app/routes/export.py"],
        detected_routes=["GET /export"],
        key_symbols=[]
    )
    impact = task_impact_service.generate_mock_impact(summary, "Add CSV export endpoint")
    simulations = strategy_simulator_service.simulate_strategies(summary, impact, "Add CSV export endpoint")
    
    assert len(simulations) == 3
    profiles = [s.profile for s in simulations]
    assert CandidateProfileEnum.AI_DEPENDENT in profiles
    assert CandidateProfileEnum.NAIVE_AI_ASSISTED in profiles
    assert CandidateProfileEnum.STRONG_AI_NATIVE in profiles
    
    # Check AI-Dependent profile has high delegation
    ai_dep = next(s for s in simulations if s.profile == CandidateProfileEnum.AI_DEPENDENT)
    assert ai_dep.estimated_delegation == "90%"
    assert len(ai_dep.missed_risks) > 0

def test_signal_evaluator_weak_task():
    summary = RepoContextSummary(
        repo_name="sample-app",
        total_files=2,
        file_tree=["app/main.py"],
        detected_routes=["GET /export"],
        key_symbols=[]
    )
    task = "Add a CSV export endpoint for user transaction history."
    impact = task_impact_service.generate_mock_impact(summary, task)
    simulations = strategy_simulator_service.simulate_strategies(summary, impact, task)
    report = signal_evaluation_service.evaluate_signal_health(summary, impact, simulations, task)
    
    assert isinstance(report, SignalHealthReport)
    assert report.ai_solvability.score >= 80
    assert len(report.ai_solvability.contributing_evidence) > 0
    assert len(report.reasoning_signal.contributing_evidence) > 0
    assert "Weak Signal" in report.verdict

def test_signal_evaluator_strong_task():
    summary = RepoContextSummary(
        repo_name="sample-app",
        total_files=5,
        file_tree=["app/main.py", "app/middleware/auth.py", "app/services/stream.py"],
        detected_routes=["GET /export"],
        key_symbols=[]
    )
    task = "Add streaming CSV export preserving RAM usage under 50MB and integrating with custom middleware."
    impact = task_impact_service.generate_mock_impact(summary, task)
    simulations = strategy_simulator_service.simulate_strategies(summary, impact, task)
    report = signal_evaluation_service.evaluate_signal_health(summary, impact, simulations, task)
    
    assert isinstance(report, SignalHealthReport)
    assert report.ai_solvability.score < 50
    assert report.overall_health_score > 50
    assert "Strong Signal" in report.verdict
