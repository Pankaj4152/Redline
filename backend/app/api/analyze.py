from fastapi import APIRouter, HTTPException, status
from app.models.schemas import AnalysisRequest, FullAssessmentResult
from app.services.orchestrator import orchestrator_service

router = APIRouter()


@router.post(
    "/analyze",
    response_model=FullAssessmentResult,
    status_code=status.HTTP_200_OK,
    summary="Analyze Coding Assessment Task",
    description="Red-teams a proposed coding assessment task against a GitHub repository, evaluating AI solvability, reasoning signal, and generating evidence-backed task upgrades."
)
async def analyze_assessment(request: AnalysisRequest) -> FullAssessmentResult:
    """
    HTTP POST route triggering the end-to-end Redline analysis pipeline.
    """
    try:
        result = orchestrator_service.run_analysis_pipeline(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline execution failed: {str(e)}"
        )
