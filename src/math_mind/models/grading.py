from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Readability(str, Enum):
    CLEAR = "CLEAR"
    PARTIAL = "PARTIAL"
    UNCLEAR = "UNCLEAR"

class QuestionResult(BaseModel):
    question: str = Field(..., description="The original question text or number")
    student_answer: str = Field(..., description="What the student wrote")
    correct_answer: str = Field(..., description="The correct answer derived by AI")
    readability: Readability = Field(..., description="Is the handwriting clear?")
    grade: float = Field(..., ge=0, le=100) # Grade must be between 0 and 100
    notes: Optional[str] = None # Any additional comments from the grading engine, e.g. "Partially correct due to minor calculation error."

class GradingResult(BaseModel):
    results: List[QuestionResult]