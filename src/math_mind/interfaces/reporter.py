from abc import ABC, abstractmethod
from pathlib import Path

from ..models.report import BatchResult


class Reporter(ABC):
    @abstractmethod
    def generate(self, result: BatchResult, output_dir: Path) -> Path:
        """Write a report for *result* into *output_dir* and return the file path."""
        ...
