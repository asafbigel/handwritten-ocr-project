import cv2
import numpy as np
from typing import List, Tuple

def segment_digits(binary_image: np.ndarray, min_area: int = 100) -> List[Tuple[int, int, int, int]]:
    """
    Segmentation Engine (Week 8 Logic):
    Splits a binary crop (e.g., '3+5') into components ['3', '+', '5'].
    
    Args:
        binary_image: Input image (White text on Black background).
        min_area: Noise filter threshold.
        
    Returns:
        List of bounding boxes (x, y, w, h), sorted Left-to-Right.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,6))
    processed = cv2.dilate(binary_image, kernel, iterations=1)
    # 1. Find Contours (Outer shape only)
    contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    valid_items = []
    
    # 2. Filter Noise
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w * h > min_area:
            valid_items.append((x, y, w, h))
            
    # 3. Sort Left-to-Right (Safe for single-line crops)
    return sorted(valid_items, key=lambda item: item[0])