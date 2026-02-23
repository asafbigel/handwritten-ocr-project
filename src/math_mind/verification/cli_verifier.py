import cv2
import numpy as np

from ..interfaces.verifier import Verifier


class CliVisualVerifier(Verifier):
    """
    Shows the original and anonymised images side-by-side in an OpenCV window
    and asks the teacher to approve or reject via a Y/N prompt.
    """

    def verify(
        self,
        original: np.ndarray,
        anonymized: np.ndarray,
        name: str,
    ) -> bool:
        combined = np.hstack([original, anonymized])
        window = f"Verify: {name}  |  left = original   right = anonymised"
        cv2.imshow(window, combined)
        cv2.waitKey(1)  # render the window without blocking

        answer = input(
            f"[Verify] Approve anonymisation for '{name}'? [Y/n]: "
        ).strip().lower()

        cv2.destroyWindow(window)
        return answer in ("", "y", "yes")
