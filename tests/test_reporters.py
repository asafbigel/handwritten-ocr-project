"""Tests for CsvReporter and JsonReporter."""

import csv
import json
from pathlib import Path

from math_mind.models.grading import GradingResult
from math_mind.models.report import BatchResult, ExamReport
from math_mind.reporting.csv_reporter import CsvReporter
from math_mind.reporting.json_reporter import JsonReporter


def _make_batch(tmp_path: Path, grading_result: GradingResult) -> BatchResult:
    return BatchResult(
        folder=tmp_path / "class_a",
        total=1,
        graded=1,
        failed=0,
        reports=[
            ExamReport(
                exam_id="exam_001",
                image_path=tmp_path / "exam_001.jpg",
                grading_result=grading_result,
                status="GRADED",
            )
        ],
    )


def test_csv_reporter_creates_file(
    tmp_path: Path, sample_grading_result: GradingResult
) -> None:
    batch = _make_batch(tmp_path, sample_grading_result)
    out = CsvReporter().generate(batch, tmp_path / "out")
    assert out.exists()


def test_csv_reporter_correct_row_count(
    tmp_path: Path, sample_grading_result: GradingResult
) -> None:
    batch = _make_batch(tmp_path, sample_grading_result)
    out = CsvReporter().generate(batch, tmp_path / "out")
    rows = list(csv.reader(out.open()))
    assert len(rows) == 2  # header + 1 exam


def test_json_reporter_creates_valid_json(
    tmp_path: Path, sample_grading_result: GradingResult
) -> None:
    batch = _make_batch(tmp_path, sample_grading_result)
    out = JsonReporter().generate(batch, tmp_path / "out")
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["graded"] == 1
    assert len(data["reports"]) == 1


def test_json_reporter_includes_questions(
    tmp_path: Path, sample_grading_result: GradingResult
) -> None:
    batch = _make_batch(tmp_path, sample_grading_result)
    out = JsonReporter().generate(batch, tmp_path / "out")
    data = json.loads(out.read_text())
    assert data["reports"][0]["grading_result"]["questions"]


def test_reporters_create_output_dir(
    tmp_path: Path, sample_grading_result: GradingResult
) -> None:
    batch = _make_batch(tmp_path, sample_grading_result)
    deep = tmp_path / "a" / "b" / "c"
    CsvReporter().generate(batch, deep)
    assert deep.exists()


def test_reporters_handle_failed_exam(tmp_path: Path) -> None:
    batch = BatchResult(
        folder=tmp_path / "class_b",
        total=1,
        graded=0,
        failed=1,
        reports=[
            ExamReport(
                exam_id="bad_exam",
                image_path=tmp_path / "bad.jpg",
                grading_result=None,
                status="FAILED",
                errors=["Could not read image"],
            )
        ],
    )
    out_csv = CsvReporter().generate(batch, tmp_path / "out")
    out_json = JsonReporter().generate(batch, tmp_path / "out")
    assert out_csv.exists()
    assert out_json.exists()
