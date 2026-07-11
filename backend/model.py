from pydantic import BaseModel
from typing import List, Dict
from enum import Enum

class PreferenceEnum(str, Enum):
    LIKE = "like"
    NORMAL = "normal"
    DISLIKE = "dislike"

class SkillEnum(str, Enum):
    GOOD = "good"
    NORMAL = "normal"
    BAD = "bad"



class TagAssessment(BaseModel):
    preference: PreferenceEnum
    skill: SkillEnum

class RecommendRequest(BaseModel):
    languages: List[str]
    tag_assessments: Dict[str, TagAssessment]
    target_count: int

class ProblemResponse(BaseModel):
    id: int
    title: str
    difficulty: str
    tags: List[str]
    url: str

class RecommendResponse(BaseModel):
    recommended_problems: List[ProblemResponse]
    ai_feedback: str
