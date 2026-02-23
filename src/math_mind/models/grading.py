from enum import StrEnum

from pydantic import BaseModel, Field


class Readability(StrEnum):
    CLEAR = "CLEAR"
    PARTIAL = "PARTIAL"
    UNCLEAR = "UNCLEAR"


class QuestionResult(BaseModel):
    question: str
    student_answer: str
    correct_answer: str  # AI self-solved
    readability: Readability
    grade: float = Field(ge=0.0)  # points earned for this question
    notes: str = ""


class GradingResult(BaseModel):
    questions: list[QuestionResult]
    total_score: float = Field(ge=0.0)
    max_score: float = Field(gt=0.0)
    overall_notes: str = ""
