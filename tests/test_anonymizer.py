import pytest
import numpy as np
from math_mind.anonymization.dynamic_anonymizer import DynamicRoiAnonymizer
from math_mind.interfaces.logger import Logger
from unittest.mock import patch, MagicMock


def _make_mock_logger() -> Logger:
    mock = MagicMock(spec=Logger)
    return mock


@pytest.fixture
def anonymizer():
    return DynamicRoiAnonymizer(logger=_make_mock_logger())

@pytest.fixture
def dummy_image():
    return np.full((100, 100, 3), 255, dtype=np.uint8)

def assert_valid_mask(result, original, y_start, y_end, x_start, x_end):
    roi = result[y_start:y_end, x_start:x_end]
    assert np.all(roi == 0), f"ROI [{y_start}:{y_end}, {x_start}:{x_end}] was not blackened"
    result[y_start:y_end, x_start:x_end] = 255
    assert np.array_equal(result, original), "Pixels outside the defined ROI were modified"

@patch('cv2.namedWindow')
@patch('cv2.destroyWindow')
def test_apply_mask_happy_path(mock_destroy_window, mock_named_window, anonymizer, dummy_image):
    result = anonymizer.apply_mask(dummy_image, 1, 2, 3, 4)
    assert_valid_mask(result, dummy_image, 2, 6, 1, 4)

@patch('cv2.namedWindow')
@patch('cv2.destroyWindow')
def test_apply_mask_edge_to_edge(mock_destroy_window, mock_named_window, anonymizer, dummy_image):
    result = anonymizer.apply_mask(dummy_image, 0, 0, 100, 100)
    assert_valid_mask(result, dummy_image, 0, 100, 0, 100)

@patch('cv2.namedWindow')
@patch('cv2.destroyWindow')
def test_apply_mask_clipping_spillover(mock_destroy_window, mock_named_window, anonymizer, dummy_image):
    res_x = anonymizer.apply_mask(dummy_image, 90, 10, 20, 10)
    assert_valid_mask(res_x, dummy_image, 10, 20, 90, 100)
    
    res_y = anonymizer.apply_mask(dummy_image, 10, 90, 10, 20)
    assert_valid_mask(res_y, dummy_image, 90, 100, 10, 20)

@patch('cv2.namedWindow')
@patch('cv2.destroyWindow')
def test_apply_mask_invalid_coordinates(mock_destroy_window, mock_named_window, anonymizer, dummy_image):    
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

@patch("cv2.namedWindow")
@patch("cv2.destroyWindow")
@patch("cv2.selectROI")
def test_anonymize_valid_selection(mock_select, mock_destroy, mock_named_window, anonymizer, dummy_image):
    # Mock: Simulate a valid user ROI selection (x, y, w, h)
    mock_select.return_value = (10, 10, 20, 20)
    
    result = anonymizer.anonymize(dummy_image)
    
    # Verify that OpenCV GUI functions were called
    assert mock_select.called
    assert mock_destroy.called
    
    # Verify the function passed the coordinates to apply_mask and blackened the correct ROI
    assert_valid_mask(result, dummy_image, 10, 30, 10, 30)

@patch("cv2.namedWindow")
@patch("cv2.destroyWindow")
@patch("cv2.selectROI")
def test_anonymize_cancelled_selection(mock_select, mock_destroy, mock_named_window, anonymizer, dummy_image):
    # Mock: Simulate a cancelled selection (width and height are zero)
    mock_select.return_value = (0, 0, 0, 0)
    
    result = anonymizer.anonymize(dummy_image)
    
    # Verify the original image is returned unchanged
    assert np.array_equal(result, dummy_image), "Image should not be modified if ROI selection is cancelled"