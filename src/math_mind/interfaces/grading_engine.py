from abc import ABC, abstractmethod
import numpy as np

class GradingEngine(ABC):
    """Interface for AI-powered grading tasks."""

    @abstractmethod
    def grade(self, image: np.ndarray) -> GradingResult:
        raise NotImplementedError