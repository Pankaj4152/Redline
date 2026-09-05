from app.models.schemas import RepoContextSummary, TaskRecommendation
from app.services.task_impact import task_impact_service
from app.services.strategy_simulator import strategy_simulator_service
from app.services.signal_evaluator import signal_evaluation_service
from app.services.upgrade_generator import upgrade_generator_service

def test_generate_mock_upgrade_weak_task():
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
    
    rec = upgrade_generator_service.generate_task_upgrade(summary, impact, simulations, report, task)
    
    assert isinstance(rec, TaskRecommendation)
    assert rec.original_task == task
    assert "streams" in rec.upgraded_task or "RAM" in rec.upgraded_task
    assert len(rec.added_constraints) > 0
    assert rec.rationale != ""

def test_generate_mock_upgrade_strong_task():
    summary = RepoContextSummary(
        repo_name="sample-app",
        total_files=5,
        file_tree=["app/main.py", "app/middleware/auth.py"],
        detected_routes=["GET /export"],
        key_symbols=[]
    )
    task = "Add streaming CSV export preserving RAM usage under 50MB and integrating with custom middleware."
    impact = task_impact_service.generate_mock_impact(summary, task)
    simulations = strategy_simulator_service.simulate_strategies(summary, impact, task)
    report = signal_evaluation_service.evaluate_signal_health(summary, impact, simulations, task)
    
    rec = upgrade_generator_service.generate_task_upgrade(summary, impact, simulations, report, task)
    
    assert isinstance(rec, TaskRecommendation)
    assert "unit tests" in rec.upgraded_task.lower() or "exception" in rec.upgraded_task.lower()
    assert len(rec.added_constraints) > 0
