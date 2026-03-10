import cv2
from math_mind.models.context import ExamContext
from math_mind.interfaces.verifier import Verifier
from math_mind.interfaces.grading_engine import GradingEngine
from math_mind.interfaces.anonymizer import Anonymizer
import logging

logger = logging.getLogger(__name__)

class GradingOrchestrator:
    def __init__(self, verifier: Verifier, engine: GradingEngine, anonymizer: Anonymizer):
        self.verifier = verifier
        self.engine = engine
        self.anonymizer = anonymizer

    def process_exam(self, image_path: str) -> ExamContext:
        logger.info(f"Starting pipeline for: {image_path}")
        
        # 1. Load (NFR1 - We load directly to memory)
        raw_image = cv2.imread(image_path)
        if raw_image is None:
            raise ValueError(f"Could not load image at {image_path}")
            
        context = ExamContext(raw_image=raw_image)

        # 2. Anonymize
        logger.info("Applying mask to hide PII...")
        context.anonymized_image = self.anonymizer.anonymize(context.raw_image)

        # 3. Verify
        logger.info("Waiting for human verification...")
        context.is_approved = self.verifier.verify(context.raw_image, context.anonymized_image, image_path)
        
        if not context.is_approved:
            logger.warning("[!] Human rejected the image. Aborting.")
            return context

        # 4. Grade
        logger.info("Image approved. Sending to AI Grading Engine...")
        context.grading_result = self.engine.grade(context.anonymized_image)

        logger.info("Pipeline completed successfully!")
        return context