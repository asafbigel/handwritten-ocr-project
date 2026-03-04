import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from math_mind.models.grading import GradingResult, QuestionResult, Readability

@pytest.fixture
def mock_data():
    """Fixture that loads our predefined inputs/outputs for the tests."""
    fixture_path = Path(__file__).parent / "fixtures" / "mock_gemini_outputs.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_valid_grading_result_parsing(mock_data):
    """Test that a fully valid JSON successfully parses into our Pydantic models."""
    valid_json = mock_data["valid_response"]
    
    # Act
    result = GradingResult.model_validate(valid_json)
    
    # Assert
    assert len(result.results) == 3
    assert result.results[0].question == "2x + 5 = 15"
    assert result.results[0].student_answer == "x = 5"
    assert result.results[0].correct_answer == "x = 5"
    assert result.results[0].readability == Readability.CLEAR
    assert result.results[0].grade == 100.0
    assert type(result.results[0].grade) == float

    assert result.results[1].question == "3y - 2 = 7"
    assert result.results[1].student_answer == "y = 2"
    assert result.results[1].correct_answer == "y = 3"
    assert result.results[1].readability == Readability.PARTIAL
    assert result.results[1].grade == 0.0
    assert type(result.results[1].grade) == float

    assert result.results[2].question == "3y - 2 = 7"
    assert result.results[2].student_answer == "3"
    assert result.results[2].correct_answer == "y = 3"
    assert result.results[2].readability == Readability.PARTIAL
    assert result.results[2].grade == 95.3
    assert type(result.results[2].grade) == float

def test_invalid_readability_enum_raises_error(mock_data):
    """Test that FR1.5 enforces the Readability Enum strictly."""
    invalid_json = mock_data["invalid_readability"]
    
    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        GradingResult.model_validate(invalid_json)
    
    assert "Input should be 'CLEAR', 'PARTIAL' or 'UNCLEAR'" in str(exc_info.value)

def test_invalid_grade_bounds_raises_error(mock_data):
    """Test that grades strictly stay between 0 and 100."""
    invalid_json = mock_data["invalid_grade_bounds"]
    
    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        GradingResult.model_validate(invalid_json)
    
    assert "Input should be less than or equal to 100" in str(exc_info.value)

def test_missing_required_field_raises_error(mock_data):
    """Test that missing the 'student_answer' field blocks validation."""
    invalid_json = mock_data["missing_required_field"]
    
    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        GradingResult.model_validate(invalid_json)
    
    assert "student_answer" in str(exc_info.value)
    assert "Field required" in str(exc_info.value)