from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import numpy as np

from .grading import GradingResult


class ExamStatus(StrEnum):
    PENDING = "PENDING"
    ANONYMIZED = "ANONYMIZED"
    VERIFIED = "VERIFIED"
    GRADED = "GRADED"
    FAILED = "FAILED"


@dataclass
class ExamContext:
    """Mutable pipeline object passed through each processing stage."""

    image_path: Path
    original_image: np.ndarray
    anonymized_image: np.ndarray | None = None
    anonymization_verified: bool = False
    grading_result: GradingResult | None = None
    status: ExamStatus = ExamStatus.PENDING
    errors: list[str] = field(default_factory=list)
