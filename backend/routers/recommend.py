from fastapi import APIRouter, HTTPException
from model import RecommendRequest, RecommendResponse

router = APIRouter()

@router.post("/recommend")
def recommend_problems(request: RecommendRequest) -> RecommendResponse:
    return RecommendResponse(
        recommended_problems=[],
        ai_feedback="N/A"
    )
