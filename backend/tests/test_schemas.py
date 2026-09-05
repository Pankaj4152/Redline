import os
import tempfile
import pytest
from pydantic import ValidationError
from app.models.schemas import (
    AnalysisRequest,
    MetricScore,
    LevelEnum,
    SignalHealthReport,
    CandidateProfileEnum,
    SimulationProfileResult,
    TaskRecommendation,
    FullAssessmentResult
)

def test_valid_analysis_request():
    req = AnalysisRequest(
        repo_url="https://github.com/fastapi/fastapi",
        branch="main",
        task_description="Add a new OAuth2 middleware endpoint to handle JWT rotation."
    )
    assert req.repo_url == "https://github.com/fastapi/fastapi"
    assert req.branch == "main"

def test_invalid_github_url_rejection():
    with pytest.raises(ValidationError) as excinfo:
        AnalysisRequest(
            repo_url="https://notgithub.com/bad/repo",
            task_description="Add feature x to repository."
        )
    assert "Invalid GitHub URL" in str(excinfo.value)

def test_short_task_description_rejection():
    with pytest.raises(ValidationError):
        AnalysisRequest(
            repo_url="https://github.com/fastapi/fastapi",
            task_description="Too short"
        )

def test_metric_score_requires_evidence():
    with pytest.raises(ValidationError):
        # Empty contributing_evidence should fail validation
        MetricScore(
            score=85,
            level=LevelEnum.HIGH,
            contributing_evidence=[]
        )

def test_full_assessment_result_serialization():
    metric = MetricScore(
        score=85,
        level=LevelEnum.HIGH,
        contributing_evidence=["Raw prompt solves endpoint without repo inspection."]
    )
    report = SignalHealthReport(
        overall_health_score=40,
        verdict="Weak Signal",
        ai_solvability=metric,
        reasoning_signal=metric,
        repo_depth=metric,
        architectural_judgment=metric,
        verification_requirement=metric
    )
    simulation = SimulationProfileResult(
        profile=CandidateProfileEnum.AI_DEPENDENT,
        success_likelihood=LevelEnum.HIGH,
        estimated_delegation="90%",
        reasoning_summary="Delegates entire task to raw LLM prompt.",
        missed_risks=["No streaming validation"]
    )
    rec = TaskRecommendation(
        original_task="Add CSV endpoint",
        upgraded_task="Add streaming CSV endpoint with 50MB memory limit",
        rationale="Forces candidate to handle memory limits."
    )
    result = FullAssessmentResult(
        job_id="job_123",
        report=report,
        simulations=[simulation],
        recommendations=rec
    )
    
    data = result.model_dump()
    assert data["job_id"] == "job_123"
    assert "heuristic design diagnostic" in data["diagnostic_disclaimer"]
    assert data["simulations"][0]["profile"] == "AI-Dependent Engineer"

def test_branch_option_injection_rejection():
    with pytest.raises(ValidationError) as excinfo:
        AnalysisRequest(
            repo_url="https://github.com/fastapi/fastapi",
            branch="--config=core.sshCommand=calc.exe",
            task_description="Add a new OAuth2 middleware endpoint."
        )
    assert "Branch name cannot start with a hyphen" in str(excinfo.value)

def test_path_traversal_local_path_rejection():
    # Use parent directory of temp dir which exists but is outside application workspace
    outside_dir = os.path.realpath(os.path.join(tempfile.gettempdir(), ".."))
    with pytest.raises(ValidationError) as excinfo:
        AnalysisRequest(
            repo_url=outside_dir,
            task_description="Add a new OAuth2 middleware endpoint."
        )
    assert "must reside within the application workspace" in str(excinfo.value)
