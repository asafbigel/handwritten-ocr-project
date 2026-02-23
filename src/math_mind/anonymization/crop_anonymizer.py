import numpy as np

from ..interfaces.anonymizer import Anonymizer


class CropAnonymizer(Anonymizer):
    """
    Fills a static rectangular region with a solid colour.

    The region is defined at construction time as ``(x, y, width, height)``
    in pixel coordinates (same convention as OpenCV ``cv2.rectangle``).
    Each folder of exams gets its own ``CropAnonymizer`` instance so that
    the anonymisation rectangle can differ per class / exam sheet layout.
    """

    def __init__(
        self,
        region: tuple[int, int, int, int],
        fill_color: tuple[int, int, int] = (0, 0, 0),
    ) -> None:
        """
        Args:
            region: ``(x, y, width, height)`` of the area to black out.
            fill_color: BGR fill colour (default: black).
        """
        self.region = region
        self.fill_color = fill_color

    def anonymize(self, image: np.ndarray) -> np.ndarray:
        """Return a copy of *image* with *region* filled by *fill_color*."""
        result = image.copy()
        x, y, w, h = self.region
        result[y : y + h, x : x + w] = self.fill_color
        return result
