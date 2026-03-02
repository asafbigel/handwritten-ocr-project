from abc import ABC, abstractmethod
from numpy import ndarray

class Verifier(ABC):
    """Interface for verifying the authenticity of exam images (e.g., checking for tampering)."""

    @abstractmethod
    def verify(self, original: ndarray, anonymized: ndarray, name: str) -> bool:
        raise NotImplementedError