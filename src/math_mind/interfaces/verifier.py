from abc import ABC, abstractmethod

import numpy as np


class Verifier(ABC):
    @abstractmethod
    def verify(self, original: np.ndarray, anonymized: np.ndarray, name: str) -> bool:
        """Return True if the teacher approves the anonymisation, False to reject."""
        ...
