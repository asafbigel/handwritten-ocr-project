"""Tests for GradingOrchestrator."""

from pathlib import Path

from math_mind.anonymization.crop_anonymizer import CropAnonymizer
from math_mind.interfaces.grading_engine import GradingEngine
from math_mind.interfaces.verifier import Verifier
from math_mind.pipeline.orchestrator import GradingOrchestrator


def _make_orchestrator(
    engine: GradingEngine,
    verifier: Verifier,
    region: tuple[int, int, int, int] = (0, 0, 10, 10),
) -> GradingOrchestrator:
    return GradingOrchestrator(
        anonymizer=CropAnonymizer(region),
        engine=engine,
        verifier=verifier,
        reporters=[],
    )


def test_grades_all_images_in_folder(
    tmp_image_folder: Path,
    mock_engine: GradingEngine,
    auto_verifier: Verifier,
    tmp_path: Path,
) -> None:
    orch = _make_orchestrator(mock_engine, auto_verifier)
    result = orch.process_folder(tmp_image_folder, tmp_path / "output")
    assert result.graded == result.total
    assert result.failed == 0


def test_marks_failed_on_corrupt_image(
    mock_engine: GradingEngine,
    auto_verifier: Verifier,
    tmp_path: Path,
) -> None:
    bad_dir = tmp_path / "bad_class"
    bad_dir.mkdir()
    (bad_dir / "bad.jpg").write_bytes(b"not an image")

    orch = _make_orchestrator(mock_engine, auto_verifier)
    result = orch.process_folder(bad_dir, tmp_path / "output")
    assert result.failed == 1


def test_rejection_marks_failed(
    tmp_image_folder: Path,
    mock_engine: GradingEngine,
    tmp_path: Path,
) -> None:
    """A verifier that always rejects should cause all exams to fail."""

    from math_mind.interfaces.verifier import Verifier

    class RejectAll(Verifier):
        def verify(self, *_: object) -> bool:
            return False

    orch = _make_orchestrator(mock_engine, RejectAll())
    result = orch.process_folder(tmp_image_folder, tmp_path / "output")
    assert result.failed == result.total
    assert result.graded == 0


def test_per_folder_anonymisers_are_independent(
    tmp_image_folder: Path,
    mock_engine: GradingEngine,
    auto_verifier: Verifier,
    tmp_path: Path,
) -> None:
    """
    Two orchestrators with different crop regions must each process the
    folder successfully — demonstrating the per-folder design works.
    """
    for region in [(0, 0, 20, 20), (50, 50, 30, 30)]:
        orch = _make_orchestrator(mock_engine, auto_verifier, region=region)
        result = orch.process_folder(tmp_image_folder, tmp_path / "output")
        assert result.graded == result.total
