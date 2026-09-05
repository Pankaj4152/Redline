import re
from enum import Enum
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CandidateProfileEnum(str, Enum):
    """The 3 simulated AI-assisted candidate profiles in Redline."""
    AI_DEPENDENT = "AI-Dependent Engineer"
    NAIVE_AI_ASSISTED = "Naive AI-Assisted Engineer"
    STRONG_AI_NATIVE = "Strong AI-Native Engineer"


class LevelEnum(str, Enum):
    """Impact and rating level classifications."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class AnalysisRequest(BaseModel):
    """
    HTTP Request Payload for analyzing a coding assessment.
    """
    repo_url: str = Field(
        ...,
        description="Public GitHub Repository URL (e.g. https://github.com/org/repo)",
        examples=["https://github.com/fastapi/fastapi"]
    )
    branch: str = Field(
        default="main",
        description="Target branch to clone and analyze"
    )
    task_description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The candidate assessment task prompt to red-team"
    )

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v: str) -> str:
        v = v.strip()
        # Allow local folder paths for local dev testing
        if v.startswith(".") or v.startswith("/") or "://" not in v:
            return v
        
        # Regex for HTTPS GitHub repository URLs
        github_pattern = r"^https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+(?:\.git)?$"
        if not re.match(github_pattern, v):
            raise ValueError(
                "Invalid GitHub URL. Must match pattern: https://github.com/owner/repository"
            )
        return v


class RepoSource(BaseModel):
    """Internal model for cloned or local repository metadata."""
    url: str
    branch: str = "main"
    is_local: bool = False


# ---------------------------------------------------------------------------
# Repository Extraction & Context Schemas
# ---------------------------------------------------------------------------

class RepoSymbol(BaseModel):
    """Extracted AST code symbol (route handler, class, or function)."""
    name: str
    symbol_type: str = Field(..., description="e.g. endpoint, class, function")
    file_path: str


class RepoContextSummary(BaseModel):
    """Sanitized repository context outline prepared for LLM prompts."""
    repo_name: str
    total_files: int
    file_tree: list[str]
    detected_routes: list[str] = Field(default_factory=list)
    key_symbols: list[RepoSymbol] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Metric & Signal Scoring Schemas
# ---------------------------------------------------------------------------

class MetricScore(BaseModel):
    """
    Individual evaluation dimension score with mandatory qualitative evidence linkage.
    """
    score: int = Field(..., ge=0, le=100, description="Heuristic score between 0 and 100")
    level: LevelEnum
    contributing_evidence: list[str] = Field(
        ...,
        min_length=1,
        description="Mandatory list of qualitative evidence statements explaining the score"
    )


class SignalHealthReport(BaseModel):
    """
    Diagnostic assessment health report covering all 5 Redline dimensions.
    """
    overall_health_score: int = Field(..., ge=0, le=100)
    verdict: str = Field(..., description="e.g. Weak Signal - Highly AI-Delegable")
    ai_solvability: MetricScore
    reasoning_signal: MetricScore
    repo_depth: MetricScore
    architectural_judgment: MetricScore
    verification_requirement: MetricScore


# ---------------------------------------------------------------------------
# Simulation & Recommendation Schemas
# ---------------------------------------------------------------------------

class SimulationProfileResult(BaseModel):
    """Result of an LLM-simulated candidate profile solving the task."""
    profile: CandidateProfileEnum
    success_likelihood: LevelEnum
    estimated_delegation: str = Field(..., description="e.g. 90%")
    reasoning_summary: str
    missed_risks: list[str] = Field(default_factory=list)
    inspected_files: list[str] = Field(default_factory=list)


class TaskRecommendation(BaseModel):
    """Actionable task upgrade recommendation."""
    original_task: str
    upgraded_task: str
    rationale: str
    added_constraints: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Full Output Schema
# ---------------------------------------------------------------------------

class FullAssessmentResult(BaseModel):
    """
    Complete end-to-end response returned by Redline analysis endpoints.
    """
    job_id: str
    status: str = "completed"
    diagnostic_disclaimer: str = (
        "The Assessment Health Score is a heuristic design diagnostic based on static code structure "
        "and simulated AI solving strategies. It is not a statistically validated measurement or candidate prediction."
    )
    repo_summary: RepoContextSummary | None = None
    report: SignalHealthReport
    simulations: list[SimulationProfileResult]
    recommendations: TaskRecommendation
