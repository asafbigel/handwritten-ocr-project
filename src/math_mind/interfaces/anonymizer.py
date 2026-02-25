from abc import ABC, abstractmethod
import numpy as np

class Anonymizer(ABC):
    """Interface for anonymizing exam images (e.g., hiding student names)."""

    @abstractmethod
    def anonymize(self, image: np.ndarray) -> np.ndarray:
        raise NotImplementedError