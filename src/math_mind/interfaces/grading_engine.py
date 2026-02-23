from abc import ABC, abstractmethod

import numpy as np

from ..models.grading import GradingResult


class GradingEngine(ABC):
    @abstractmethod
    def grade(self, image: np.ndarray) -> GradingResult:
        """Grade a single (anonymised) exam image and return structured results."""
        ...
