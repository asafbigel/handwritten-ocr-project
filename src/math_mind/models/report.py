from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .grading import GradingResult


@dataclass
class ExamReport:
    exam_id: str
    image_path: Path
    grading_result: GradingResult | None
    status: str
    errors: list[str] = field(default_factory=list)


@dataclass
class BatchResult:
    folder: Path
    reports: list[ExamReport] = field(default_factory=list)
    processed_at: datetime = field(default_factory=datetime.now)
    total: int = 0
    graded: int = 0
    failed: int = 0
