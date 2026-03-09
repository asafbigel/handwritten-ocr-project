"""
Unit tests for the GeminiGradingEngine.
Validates API interaction, correct mapping of external SDK errors to internal domain exceptions,
and verifies the successful parsing of structured outputs (Pydantic models).
"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import numpy as np
import pytest

from math_mind.models.grading import GradingResult, Readability
from math_mind.engines.gemini_engine import GeminiGradingEngine
from math_mind.engines.exceptions import ConfigurationError
from google.genai import errors as genai_errors


# --- Fixtures ---

@pytest.fixture
def mock_image() -> np.ndarray:
    """
    Provides a dummy 100x100 RGB numpy array to simulate an input image.
    This avoids needing actual image files on disk during unit testing.
    """
    return np.zeros((100, 100, 3), dtype=np.uint8)

@pytest.fixture
def valid_grading_result_object() -> GradingResult:
    """
    Loads a predefined valid JSON response from the fixtures directory
    and converts it into a valid Pydantic GradingResult object.
    This accurately simulates the 'parsed' object returned by the Google SDK 
    when using Structured Output (FR1.5).
    """
    fixture_path = Path(__file__).parent / "fixtures" / "mock_gemini_outputs.json"
    
    with open(fixture_path, "r", encoding="utf-8") as f:
        mock_data = json.load(f)
        
    valid_dict = mock_data["valid_response"]
    return GradingResult.model_validate(valid_dict)


# --- Tests ---

@patch("math_mind.engines.gemini_engine.genai.Client") 
def test_gemini_engine_happy_flow(mock_client_class, mock_image, valid_grading_result_object):
    """
    Tests the standard successful execution path of the Gemini grading engine.
    Verifies that the engine sends the request and correctly returns the strongly-typed 
    Pydantic object without altering the parsed data.
    """
    # 1. Arrange: Setup the mock to simulate Google SDK's structured output
    mock_client_instance = MagicMock()
    mock_response = MagicMock()
    # The SDK automatically places the Pydantic object into the 'parsed' attribute
    mock_response.parsed = valid_grading_result_object 
    
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_client_class.return_value = mock_client_instance
    
    engine = GeminiGradingEngine(api_key="dummy_key", model_name="gemini-2.5-flash")
    
    # 2. Act: Execute the grading process
    result = engine.grade(mock_image)
    
    # 3. Assert: Verify the SDK was called and the return type is strictly enforced
    mock_client_instance.models.generate_content.assert_called_once()
    assert isinstance(result, GradingResult), "Engine must return a GradingResult object"
    assert len(result.results) == len(valid_grading_result_object.results), "Expected same number of graded questions based on the fixture"
    assert result.results[0].readability == Readability.CLEAR


def test_gemini_engine_invalid_credentials_raises_error(mock_image):
    """
    Tests the engine's error handling for authentication or configuration issues.
    Verifies that external SDK errors (e.g., HTTP 400 API_KEY_INVALID) are caught
    and properly mapped to the internal domain 'ConfigurationError' (NFR3).
    """
    with patch("math_mind.engines.gemini_engine.genai.Client") as mock_client_class:
        mock_client_instance = MagicMock()
        
        # Google's ClientError __init__ expects a complex raw HTTP response object.
        # To simplify testing, we create a lightweight subclass that bypasses __init__ 
        # but correctly behaves like a ClientError and outputs the '400' status.
        class FakeClientError(genai_errors.ClientError):
            def __init__(self):
                pass
            def __str__(self):
                return "400 INVALID_ARGUMENT"

        # Arrange: Simulate an API key failure
        mock_client_instance.models.generate_content.side_effect = FakeClientError()
        mock_client_class.return_value = mock_client_instance
        
        engine = GeminiGradingEngine(api_key="GARBAGE_KEY", model_name="NON_EXISTENT_MODEL")
        
        # Act & Assert: Ensure the internal mapping mechanism intercepts the error
        with pytest.raises(ConfigurationError) as exc_info:
            engine.grade(mock_image)
            
        assert "API/Model Config Error" in str(exc_info.value), "Error message should contain domain context"