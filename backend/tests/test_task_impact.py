from app.models.schemas import RepoContextSummary, RepoSymbol, LevelEnum, TaskImpactResult
from app.services.task_impact import TaskImpactService, task_impact_service

def test_generate_mock_impact_low_depth():
    summary = RepoContextSummary(
        repo_name="sample-app",
        total_files=3,
        file_tree=["app/main.py", "app/routes/export.py"],
        detected_routes=["GET /export"],
        key_symbols=[RepoSymbol(name="export_data", symbol_type="function", file_path="app/routes/export.py")]
    )
    task = "Add a CSV export endpoint for user transaction history."
    result = task_impact_service.generate_mock_impact(summary, task)
    
    assert isinstance(result, TaskImpactResult)
    assert result.architectural_depth_required == LevelEnum.LOW
    assert len(result.impacted_files) > 0
    assert any("export.py" in f for f in result.impacted_files)

def test_generate_mock_impact_high_depth():
    summary = RepoContextSummary(
        repo_name="sample-app",
        total_files=5,
        file_tree=["app/main.py", "app/middleware/auth.py"],
        detected_routes=["GET /export"],
        key_symbols=[]
    )
    task = "Add streaming CSV export preserving RAM usage under 50MB and integrating with custom middleware."
    result = task_impact_service.generate_mock_impact(summary, task)
    
    assert isinstance(result, TaskImpactResult)
    assert result.architectural_depth_required == LevelEnum.HIGH
    assert len(result.potential_side_effects) > 0

def test_analyze_task_impact_service_end_to_end():
    summary = RepoContextSummary(
        repo_name="sample-app",
        total_files=2,
        file_tree=["app/main.py"],
        detected_routes=["GET /health"],
        key_symbols=[]
    )
    task = "Refactor user authentication service to support JWT refresh tokens."
    result = task_impact_service.analyze_task_impact(summary, task)
    
    assert isinstance(result, TaskImpactResult)
    assert result.summary != ""
    assert isinstance(result.impacted_modules, list)
