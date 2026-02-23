from abc import ABC, abstractmethod

from ..models.context import ExamContext


class ImageProcessor(ABC):
    """
    Phase 2 placeholder.

    Implementations will perform image-level transformations (deskewing,
    contrast enhancement, etc.) on the ExamContext before anonymisation.
    """

    @abstractmethod
    def process(self, context: ExamContext) -> ExamContext:
        """Transform *context.original_image* and return the updated context."""
        ...
