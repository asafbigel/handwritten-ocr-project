import typer
import logging
from typing import Annotated
from math_mind.config import settings
from math_mind.pipeline.orchestrator import GradingOrchestrator
from math_mind.engines.gemini_engine import GeminiGradingEngine
from math_mind.verification.cli_verifier import CliVisualVerifier
from math_mind.anonymization.dynamic_anonymizer import DynamicRoiAnonymizer
from math_mind.utils.logger_setup import configure_logging

# Configure logging
configure_logging(logging.DEBUG)
logger = logging.getLogger(__name__)

app = typer.Typer(help="Math-Mind Hybrid Grader CLI")

@app.command()
def grade(
    image_path: Annotated[str, typer.Argument(help="Path to the scanned exam image")]
):
    """Run the full anonymization, verification, and grading pipeline."""
    logger.info(f"Starting pipeline for: {image_path}")
    
    # Dependency Injection wiring
    verifier = CliVisualVerifier()
    anonymizer = DynamicRoiAnonymizer()
    engine = GeminiGradingEngine(
        api_key=settings.gemini_api_key,
        model_name=settings.gemini_model
    )
    
    
    # Create and run the orchestrator
    # verifier: Verifier, engine: GradingEngine, anonymizer: Anonymizer
    orchestrator = GradingOrchestrator(verifier=verifier, engine=engine, anonymizer=anonymizer)
    
    try:
        context = orchestrator.process_exam(image_path)
        
        # Output the results!
        if context.is_approved:
            if context.grading_result:
                logger.info("\n--- GRADING REPORT ---")
                for res in context.grading_result.results:
                    logger.info(f"Q: {res.question}")
                    logger.info(f"Student: {res.student_answer}")
                    logger.info(f"Correct: {res.correct_answer}")
                    logger.info(f"Grade: {res.grade} ({res.readability.name})")
                    logger.info("-" * 20)
            else:
                logger.warning("No grading result available.")
        else:
            logger.warning("Image was rejected by the human verifier. No grading performed.")
    except Exception as e:
        logger.error(f"\n[ERROR] Pipeline failed: {e}")

if __name__ == "__main__":
    app()