"""Shared pytest fixtures for the Math-Mind test suite."""

import numpy as np
import pytest

from math_mind.interfaces.grading_engine import GradingEngine
from math_mind.interfaces.verifier import Verifier
from math_mind.models.grading import GradingResult, QuestionResult, Readability

# ---------------------------------------------------------------------------
# Image fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_image() -> np.ndarray:
    """200 × 300 white BGR image."""
    return np.full((300, 200, 3), 255, dtype=np.uint8)


# ---------------------------------------------------------------------------
# Domain-model fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_grading_result() -> GradingResult:
    return GradingResult(
        questions=[
            QuestionResult(
                question="2 + 2",
                student_answer="4",
                correct_answer="4",
                readability=Readability.CLEAR,
                grade=5.0,
            )
        ],
        total_score=5.0,
        max_score=5.0,
    )


# ---------------------------------------------------------------------------
# Mock implementations
# ---------------------------------------------------------------------------


class _MockGradingEngine(GradingEngine):
    def __init__(self, result: GradingResult) -> None:
        self._result = result

    def grade(self, image: np.ndarray) -> GradingResult:  # noqa: ARG002
        return self._result


@pytest.fixture()
def mock_engine(sample_grading_result: GradingResult) -> GradingEngine:
    return _MockGradingEngine(sample_grading_result)


class _AutoApproveVerifier(Verifier):
    def verify(  # noqa: ARG002
        self,
        original: np.ndarray,
        anonymized: np.ndarray,
        name: str,
    ) -> bool:
        return True


@pytest.fixture()
def auto_verifier() -> Verifier:
    return _AutoApproveVerifier()


# ---------------------------------------------------------------------------
# File-system fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_image_folder(tmp_path: any, sample_image: np.ndarray):  # type: ignore[type-arg]
    """A temp folder containing two valid JPEG exam images."""
    import cv2

    img_dir = tmp_path / "test_class"
    img_dir.mkdir()
    cv2.imwrite(str(img_dir / "exam_001.jpg"), sample_image)
    cv2.imwrite(str(img_dir / "exam_002.jpg"), sample_image)
    return img_dir
