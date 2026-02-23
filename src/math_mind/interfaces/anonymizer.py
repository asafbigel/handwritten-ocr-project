from abc import ABC, abstractmethod

import numpy as np


class Anonymizer(ABC):
    @abstractmethod
    def anonymize(self, image: np.ndarray) -> np.ndarray:
        """Return a copy of *image* with identifying information removed."""
        ...
