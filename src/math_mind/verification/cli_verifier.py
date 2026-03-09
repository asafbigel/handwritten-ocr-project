import cv2
from numpy import ndarray
from math_mind.interfaces.verifier import Verifier


class CliVisualVerifier(Verifier):
    """
    A simple CLI-based visual verifier that displays the original and anonymized images side by side,
    and prompts the user to confirm if the anonymization is acceptable by pressing 'y' or 'n'.    
    """

    def verify(self, original: ndarray, anonymized: ndarray, name: str = "missing_name") -> bool:
        if original is None or anonymized is None:
            raise ValueError("Image array cannot be null")
        if original.size == 0 or anonymized.size == 0:
            raise ValueError("Image array cannot be empty")  
        if original.shape != anonymized.shape:
            raise ValueError("Original and anonymized images must have the same dimensions")      
        
        combined = cv2.hconcat([original, anonymized])
        window_title = f"Verification for {name} (Press 'y' to approve, 'n' to reject)"
        cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
        cv2.imshow(window_title, combined)
        
        while True:
            key = cv2.waitKey(0) & 0xFF
            if key in (ord('y'), ord('Y')):
                cv2.destroyWindow(window_title)
                return True
            elif key in (27, ord('n'), ord('N')):
                cv2.destroyWindow(window_title)
                return False