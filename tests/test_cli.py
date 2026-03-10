import logging
from typer.testing import CliRunner
from math_mind.cli import app
from math_mind.models.context import ExamContext
from math_mind.models.grading import GradingResult, QuestionResult, Readability
import numpy as np

# We use CliRunner to invoke the CLI commands in a test environment
runner = CliRunner()

def test_cli_grade_happy_flow(mocker, caplog):
    # ==========================================
    # 1. ARRANGE: Mocking the Core
    # ==========================================
    # We create a mock ExamContext that the Orchestrator will return, simulating a successful grading scenario.
    mock_context = ExamContext(raw_image=np.zeros((10,10,3), dtype=np.uint8))
    mock_context.anonymized_image = np.ones((10,10,3), dtype=np.uint8)
    mock_context.is_approved = True
    mock_context.grading_result = GradingResult(
        results=[
            QuestionResult(
                question="1+1",
                student_answer="2",
                correct_answer="2",
                readability=Readability.CLEAR,
                grade=100.0)]
                )

    mock_settings = mocker.patch("math_mind.config.get_settings")
    mock_settings.return_value.gemini_api_key = "fake_api_key"
    mock_settings.return_value.gemini_model = "fake_model"

    # We patch the GradingOrchestrator within the CLI's namespace!
    mock_orchestrator_class = mocker.patch("math_mind.cli.GradingOrchestrator")
    
    # The following line captures the *instance* that the CLI creates, so we can control its behavior
    mock_orchestrator_instance = mock_orchestrator_class.return_value
    mock_orchestrator_instance.process_exam.return_value = mock_context

    # we set the logging level to INFO for our CLI logger to capture the grading report logs
    caplog.set_level(logging.INFO, logger="math_mind.cli")
    
    result = runner.invoke(app, ["fake_path.jpg"])

    assert result.exit_code == 0
    mock_orchestrator_instance.process_exam.assert_called_once_with("fake_path.jpg")
    
    # Now we check the logs to ensure the grading report was printed as expected
    logs = caplog.text

    assert "Image was rejected by the human verifier. No grading performed." not in logs
    assert "GRADING REPORT" in logs
    assert "Q: 1+1" in logs
    assert "Student: 2" in logs
    assert "Correct: 2" in logs
    assert "(CLEAR)" in logs
    assert "Grade: 100.0" in logs
    assert result.stderr is not None or result.stderr == ""
    

def test_cli_grade_rejected_flow(mocker, caplog):
    # ==========================================
    # 1. ARRANGE: Mocking the Core
    # ==========================================
    # We create a mock ExamContext that the Orchestrator will return, simulating a successful grading scenario.
    mock_context = ExamContext(raw_image=np.zeros((10,10,3), dtype=np.uint8))
    mock_context.anonymized_image = np.ones((10,10,3), dtype=np.uint8)
    mock_context.is_approved = False

    mock_settings = mocker.patch("math_mind.config.get_settings")
    mock_settings.return_value.gemini_api_key = "fake_api_key"
    mock_settings.return_value.gemini_model = "fake_model"

    # We patch the GradingOrchestrator within the CLI's namespace!
    mock_orchestrator_class = mocker.patch("math_mind.cli.GradingOrchestrator")
    
    # The following line captures the *instance* that the CLI creates, so we can control its behavior
    mock_orchestrator_instance = mock_orchestrator_class.return_value
    mock_orchestrator_instance.process_exam.return_value = mock_context

    # we set the logging level to INFO for our CLI logger to capture the grading report logs
    caplog.set_level(logging.INFO, logger="math_mind.cli")
    
    result = runner.invoke(app, ["fake_path.jpg"])

    assert result.exit_code == 0
    mock_orchestrator_instance.process_exam.assert_called_once_with("fake_path.jpg")
    
    # Now we check the logs to ensure the grading report was printed as expected
    logs = caplog.text

    assert "Image was rejected by the human verifier. No grading performed." in logs
    assert "GRADING REPORT" not in logs
    assert "Q: 1+1" not in logs
    assert "Student: 2" not in logs
    assert "Correct: 2" not in logs
    assert "(CLEAR)" not in logs
    assert "Grade: 100.0" not in logs
    assert result.stderr is not None or result.stderr == ""

def test_cli_grade_empty_path(mocker, caplog):
    # We patch the GradingOrchestrator within the CLI's namespace!
    mock_orchestrator_class = mocker.patch("math_mind.cli.GradingOrchestrator")
    
    # The following line captures the *instance* that the CLI creates, so we can control its behavior
    mock_orchestrator_instance = mock_orchestrator_class.return_value

    result = runner.invoke(app, [])

    assert result.exit_code != 0  # Should fail due to missing argument
    assert result.stderr is not None
    mock_orchestrator_instance.process_exam.assert_not_called()