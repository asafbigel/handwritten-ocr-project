import pytest
import numpy as np
from math_mind.anonymization.dynamic_anonymizer import DynamicRoiAnonymizer

@pytest.fixture
def anonymizer():
    return DynamicRoiAnonymizer()

@pytest.fixture
def dummy_image():
    return np.full((100, 100, 3), 255, dtype=np.uint8)

def assert_valid_mask(result, original, y_start, y_end, x_start, x_end):
    roi = result[y_start:y_end, x_start:x_end]
    assert np.all(roi == 0), f"ROI [{y_start}:{y_end}, {x_start}:{x_end}] was not blackened"
    result[y_start:y_end, x_start:x_end] = 255
    assert np.array_equal(result, original), "Pixels outside the defined ROI were modified"

def test_apply_mask_happy_path(anonymizer, dummy_image):
    result = anonymizer.apply_mask(dummy_image, 1, 2, 3, 4)
    assert_valid_mask(result, dummy_image, 2, 6, 1, 4)

def test_apply_mask_edge_to_edge(anonymizer, dummy_image):
    result = anonymizer.apply_mask(dummy_image, 0, 0, 100, 100)
    assert_valid_mask(result, dummy_image, 0, 100, 0, 100)

def test_apply_mask_clipping_spillover(anonymizer, dummy_image):
    res_x = anonymizer.apply_mask(dummy_image, 90, 10, 20, 10)
    assert_valid_mask(res_x, dummy_image, 10, 20, 90, 100)
    
    res_y = anonymizer.apply_mask(dummy_image, 10, 90, 10, 20)
    assert_valid_mask(res_y, dummy_image, 90, 100, 10, 20)

def test_apply_mask_invalid_coordinates(anonymizer, dummy_image):    
    with pytest.raises(ValueError):
        anonymizer.apply_mask(dummy_image, 10, 10, -5, 10)
    with pytest.raises(ValueError):
        anonymizer.apply_mask(dummy_image, 10, 10, 10, -5)
    with pytest.raises(ValueError):
        anonymizer.apply_mask(dummy_image, 10, 10, 0, 10)
    with pytest.raises(ValueError):
        anonymizer.apply_mask(dummy_image, 10, 10, 10, 0)

    invalid_starts = [
        (-5, 10), (10, -5), (-50, 50), (15, -50),
        (150, 20), (20, 150), (100, 10), (10, 100)
    ]
    
    for x, y in invalid_starts:
        with pytest.raises(ValueError, match="Coordinates out of image bounds"):
            anonymizer.apply_mask(dummy_image, x, y, 1, 1)