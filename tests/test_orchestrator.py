import pytest
import numpy as np
from math_mind.pipeline.orchestrator import GradingOrchestrator

# Fixtures for setting up the test environment with mocks
@pytest.fixture
def orchestrator_env(mocker):
    # Setup Mocks with Default "Happy Flow" behavior
    mock_imread = mocker.patch("math_mind.pipeline.orchestrator.cv2.imread")
    mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
    
    mock_anonymizer = mocker.Mock()
    mock_anonymizer.anonymize.return_value = np.ones((100, 100, 3), dtype=np.uint8)
    
    mock_verifier = mocker.Mock()
    mock_verifier.verify.return_value = True  # Default: Teacher approves
    
    mock_engine = mocker.Mock()
    mock_engine.grade.return_value = "Mock Grading Result"
    
    orchestrator = GradingOrchestrator(
        verifier=mock_verifier, 
        engine=mock_engine, 
        anonymizer=mock_anonymizer
    )
    
    # Return all mocks and the orchestrator for use in tests
    return mock_imread, mock_anonymizer, mock_verifier, mock_engine, orchestrator

# Test the happy flow scenario
def test_process_exam_happy_flow(orchestrator_env):
    # Arrange
    imread, anonymizer, verifier, engine, orchestrator = orchestrator_env
    context = orchestrator.process_exam("valid_path.jpg")

    # Assert
    imread.assert_called_once_with("valid_path.jpg")
    assert imread.return_value is context.raw_image
    assert np.array_equal(context.raw_image, np.zeros((100, 100, 3), dtype=np.uint8))

    anonymizer.anonymize.assert_called_once_with(context.raw_image)
    assert anonymizer.anonymize.return_value is context.anonymized_image
    assert np.array_equal(context.anonymized_image, np.ones((100, 100, 3), dtype=np.uint8))

    verifier.verify.assert_called_once_with(context.raw_image, context.anonymized_image, "valid_path.jpg")
    assert verifier.verify.return_value is context.is_approved
    assert context.is_approved is True

    engine.grade.assert_called_once_with(context.anonymized_image)
    assert engine.grade.return_value is context.grading_result
    assert str(context.grading_result) == "Mock Grading Result"

def test_process_exam_invalid_image(orchestrator_env):
    # Arrange
    imread, anonymizer, verifier, engine, orchestrator = orchestrator_env
    imread.return_value = None  # Simulate failed image load
    context = None
    
    # Assert
    with pytest.raises(ValueError, match="Could not load image at invalid_path.jpg"):
        context = orchestrator.process_exam("invalid_path.jpg")
    
    imread.assert_called_once_with("invalid_path.jpg")
    assert imread.return_value is None  # Simulate failed image load
    assert context is None  # Context should be None due to failed load

    anonymizer.anonymize.assert_not_called()
    verifier.verify.assert_not_called()
    engine.grade.assert_not_called()
    

# Test that if the verifier rejects, the engine is NOT called and the process stops early
def test_process_exam_stops_when_verifier_rejects(orchestrator_env):
    # Arrange
    imread, anonymizer, verifier, engine, orchestrator = orchestrator_env
    verifier.verify.return_value = False  # Simulate teacher rejection
    context = orchestrator.process_exam("valid_path.jpg")

    # Assert
    imread.assert_called_once_with("valid_path.jpg")
    assert imread.return_value is context.raw_image
    assert np.array_equal(context.raw_image, np.zeros((100, 100, 3), dtype=np.uint8))

    anonymizer.anonymize.assert_called_once_with(context.raw_image)
    assert anonymizer.anonymize.return_value is context.anonymized_image
    assert np.array_equal(context.anonymized_image, np.ones((100, 100, 3), dtype=np.uint8))

    verifier.verify.assert_called_once_with(context.raw_image, context.anonymized_image, "valid_path.jpg")
    assert verifier.verify.return_value is context.is_approved
    assert context.is_approved is False

    engine.grade.assert_not_called()  # Engine should NOT be called if verifier rejects
    assert context.grading_result is None  # Grading result should be None if not graded