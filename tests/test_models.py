"""Tests for domain models."""

from pathlib import Path

from math_mind.models.context import ExamContext, ExamStatus
from math_mind.models.grading import GradingResult, QuestionResult, Readability
from math_mind.models.report import BatchResult, ExamReport


def test_question_result_schema() -> None:
    q = QuestionResult(
        question="3 × 3",
        student_answer="9",
        correct_answer="9",
        readability=Readability.CLEAR,
        grade=5.0,
    )
    assert q.grade == 5.0
    assert q.readability == Readability.CLEAR


def test_grading_result_roundtrip(sample_grading_result: GradingResult) -> None:
    data = sample_grading_result.model_dump()
    restored = GradingResult.model_validate(data)
    assert restored.total_score == sample_grading_result.total_score
    assert len(restored.questions) == len(sample_grading_result.questions)


def test_exam_context_status_transitions(sample_image, tmp_path: Path) -> None:
    ctx = ExamContext(image_path=tmp_path / "test.jpg", original_image=sample_image)
    assert ctx.status == ExamStatus.PENDING
    ctx.status = ExamStatus.GRADED
    assert ctx.status == ExamStatus.GRADED


def test_exam_context_errors_default_empty(sample_image, tmp_path: Path) -> None:
    ctx = ExamContext(image_path=tmp_path / "test.jpg", original_image=sample_image)
    assert ctx.errors == []


def test_batch_result_counts(tmp_path: Path) -> None:
    batch = BatchResult(folder=tmp_path, total=3, graded=2, failed=1)
    assert batch.total == 3
    assert batch.graded + batch.failed == 3


def test_exam_report_no_grading_result(tmp_path: Path) -> None:
    report = ExamReport(
        exam_id="x",
        image_path=tmp_path / "x.jpg",
        grading_result=None,
        status="FAILED",
        errors=["oops"],
    )
    assert report.grading_result is None
