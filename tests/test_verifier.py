import pytest
import numpy as np
from unittest.mock import patch 
from math_mind.verification.cli_verifier import CliVisualVerifier 

@pytest.fixture
def valid_image() -> np.ndarray:
    """Returns a valid dummy 100x100 RGB image."""
    return np.zeros((100, 100, 3), dtype=np.uint8)

@pytest.fixture
def empty_image() -> np.ndarray:
    """Returns an empty array simulating a corrupted/missing image."""
    return np.array([])


class TestCliVisualVerifier:
    
    @patch('cv2.waitKey')
    @patch('cv2.imshow')
    @pytest.mark.timeout(2)
    @pytest.mark.parametrize("key_sequence, expected_result", [('Y', True), ('y', True), ('n', False), ('N', False), (27, False),])
    def test_verify_approves_on_key(self, mock_imshow, mock_waitKey, valid_image, key_sequence, expected_result):
        # Arrange
        mock_waitKey.return_value = ord(key_sequence) if isinstance(key_sequence, str) else key_sequence
        verifier = CliVisualVerifier()
        
        # Act
        result = verifier.verify(original=valid_image, anonymized=valid_image, name="John Doe")
        
        # Assert
        assert result is expected_result
        mock_imshow.assert_called_once()
        
    @patch('cv2.imshow')
    @patch('cv2.waitKey')
    @pytest.mark.parametrize("key_sequence, expected_result", [
        # Scenario 1: Random keys, space, then OK
        ([ord('x'), 32, ord('g'), ord('Y')], True), 
        # Scenario 2: Ignore special keys like TAB and ENTER
        ([9, 13, ord('Y')], True), 
        # Scenario 3: Lowercase vs uppercase letters (depends on system support for 'y' lowercase)
        ([ord('a'), ord('b'), ord('y')], True),
        # Scenario 4: End with rejection (assuming 'N' returns False)
        ([32, ord('1'), ord('N')], False),
        # Scenario 5: Exit with ESC (note - if system ignores ESC, change to True. If it exits, keep False)
        ([27], False), 
    ])
    def test_verify_ignores_invalid_keys_until_valid(self, mock_waitKey, mock_imshow, valid_image, key_sequence, expected_result):
        # Arrange
        mock_waitKey.side_effect = key_sequence
        verifier = CliVisualVerifier()
        
        # Act
        result = verifier.verify(original=valid_image, anonymized=valid_image, name="Edge Case")
        
        # Assert
        assert result is expected_result
        assert mock_waitKey.call_count == len(key_sequence)
   
    @pytest.mark.timeout(2)
    @pytest.mark.parametrize("image1, image2, expected_message", [
        (np.zeros((100, 100, 3), dtype=np.uint8), np.array([]), "Image array cannot be empty"),
        (np.array([]), np.zeros((100, 100, 3), dtype=np.uint8), "Image array cannot be empty"),
        (None, np.zeros((100, 100, 3), dtype=np.uint8), "Image array cannot be null"),
        (np.zeros((100, 100, 3), dtype=np.uint8), None, "Image array cannot be null"),
        ])
    def test_verify_raises_value_error_on_empty_image(self, image1, image2, expected_message):
        verifier = CliVisualVerifier()
        
        # Act & Assert
        with pytest.raises(ValueError, match=expected_message):
            verifier.verify(original=image1, anonymized=image2, name="Empty Test")

    @patch('cv2.waitKey')
    @patch('cv2.imshow')
    @patch('cv2.destroyAllWindows')
    @pytest.mark.timeout(2)
    @pytest.mark.parametrize("key_sequence", ['Y','y','n', 'N',27])
    def test_verify_destroyAllWindows_on_exit_with_key(self, mock_destroyAllWindows, mock_imshow, mock_waitKey, valid_image, key_sequence):
        # Arrange
        mock_waitKey.return_value = ord(key_sequence) if isinstance(key_sequence, str) else key_sequence
        verifier = CliVisualVerifier()
        
        # Act
        result = verifier.verify(original=valid_image, anonymized=valid_image, name="Exit Test")
        
        # Assert
        mock_destroyAllWindows.assert_called_once()
        
    @pytest.mark.timeout(2)
    def test_verify_raises_value_error_on_different_dimensions(self, valid_image):
        verifier = CliVisualVerifier()
        different_dim_image = np.zeros((50, 50, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="Original and anonymized images must have the same dimensions"):
            verifier.verify(original=valid_image, anonymized=different_dim_image, name="Dimension Test")