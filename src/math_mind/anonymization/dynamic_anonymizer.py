import cv2
import numpy as np
from math_mind.interfaces.anonymizer import Anonymizer

class DynamicRoiAnonymizer(Anonymizer):
    def apply_mask(self, image: np.ndarray, x_start: int, y_start: int, width: int, height: int) -> np.ndarray:
        """
        Apply a rectangular black mask to a region of the given image.

        The mask region is defined by its top-left corner (`x_start`, `y_start`)
        and the requested `width` and `height`. If the requested region extends
        beyond the image bounds, it is clipped so that the mask stays within
        the image dimensions.

        Parameters
        ----------
        image : numpy.ndarray
            Input image array with shape (height, width, channels) or (height, width).
        x_start : int
            X-coordinate (column index) of the top-left corner of the region to mask.
        y_start : int
            Y-coordinate (row index) of the top-left corner of the region to mask.
        width : int
            Requested width of the region to mask, in pixels. Must be positive.
        height : int
            Requested height of the region to mask, in pixels. Must be positive.

        Returns
        -------
        numpy.ndarray
            A copy of the input image with the specified region set to zero (black).

        Raises
        ------
        ValueError
            If `width` or `height` is not positive, or if (`x_start`, `y_start`)
            lies outside the image bounds.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
            
        if x_start < 0 or y_start < 0 or x_start >= image.shape[1] or y_start >= image.shape[0]:
            raise ValueError("Coordinates out of image bounds")
            
        result = image.copy()
        y_end = min(y_start + height, image.shape[0])
        x_end = min(x_start + width, image.shape[1])
        result[y_start:y_end, x_start:x_end] = 0
        return result

    def anonymize(self, image: np.ndarray) -> np.ndarray:
        """Opens a window where the teacher marks the name area using the mouse, and blacks it out."""
        roi = cv2.selectROI("Select Name to Anonymize (Press ENTER to confirm)", image, showCrosshair=True, fromCenter=False)
        cv2.destroyWindow("Select Name to Anonymize (Press ENTER to confirm)")
        
        x, y, w, h = roi
        
        if w == 0 or h == 0:
            print("No ROI selected. Returning original image.")
            return image
            
        return self.apply_mask(image, x, y, w, h)