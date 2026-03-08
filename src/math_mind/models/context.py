from dataclasses import dataclass
import numpy as np
from typing import Optional
from models.grading import GradingResult

@dataclass
class ExamContext:
    """
    Holds the state of an exam as it passes through the grading pipeline.
    """
    raw_image: np.ndarray
    anonymized_image: Optional[np.ndarray] = None
    is_approved: bool = False
    grading_result: Optional[GradingResult] = None