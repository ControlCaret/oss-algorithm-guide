from fastapi import APIRouter, HTTPException, status
from model import RecommendRequest, RecommendResponse, ProblemResponse
from problems_loader import load_problems
import random

router = APIRouter()

@router.post("/recommend", status_code=status.HTTP_200_OK)
def recommend_problems(request: RecommendRequest) -> RecommendResponse:
    all_problems = load_problems()
    if not all_problems:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Problem database is empty or not loaded."
        )

    disliked = {t.lower() for t, a in request.tag_assessments.items() if a.preference == -1}
    liked = {t.lower() for t, a in request.tag_assessments.items() if a.preference == 1}

    skills = [a.skill for a in request.tag_assessments.values()]
    allowed = ["Medium", "Hard"] if sum(skills) > 0 else ["Easy", "Medium"]

    candidates = []
    for p in all_problems:
        if p.get("is_premium", False) or p.get("difficulty", "Easy") not in allowed:
            continue
        p_tags = {t.lower() for t in p.get("tags", [])}
        if not (p_tags & disliked) and (not liked or (p_tags & liked)):
            candidates.append(p)

    if not candidates:
        candidates = [p for p in all_problems if not p.get("is_premium", False) and p.get("difficulty") in allowed]

    sampled = random.sample(candidates, min(len(candidates), request.target_count)) if candidates else []

    recommended = [
        ProblemResponse(
            id=item.get("id", 0),
            title=item.get("title", ""),
            difficulty=item.get("difficulty", "Easy"),
            tags=item.get("tags", []),
            url=item.get("url", "")
        )
        for item in sampled
    ]

    return RecommendResponse(
        recommended_problems=recommended,
        ai_feedback="N/A"
    )
