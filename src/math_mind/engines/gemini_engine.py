import json
import logging
import PIL.Image
import numpy as np
from google import genai
from math_mind.interfaces.grading_engine import GradingEngine
from math_mind.models.grading import GradingResult
from math_mind.utils.retry import with_retry
from math_mind.engines.exceptions import ConfigurationError, RateLimitExceededError
from google.genai import errors as genai_errors

logger = logging.getLogger(__name__)

class GeminiGradingEngine(GradingEngine):
    def __init__(self, api_key: str, model_name: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    @with_retry(max_retries=3, base_delay=5.0)
    def grade(self, image: np.ndarray) -> GradingResult:
        pil_image = PIL.Image.fromarray(image)

        prompt = (
            "You are an expert math teacher. Solve the math problems in this image independently. "
            "Compare your solution to the student's handwritten answer. "
            "Flag every handwriting as 'CLEAR' or 'PARTIAL' or 'UNCLEAR'."
        )
        logger.info(f"Sending grading request to Gemini model '{self.model_name}'...")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, pil_image],
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': GradingResult,
                }
            )
            
            if response.parsed:
                return response.parsed
            raise ValueError("AI failed to return a valid structured response.")

        except genai_errors.ClientError as e:
            error_msg = str(e)
            if "400" in error_msg or "404" in error_msg:
                raise ConfigurationError(f"API/Model Config Error: {error_msg}")
            if "429" in error_msg:
                raise RateLimitExceededError(f"Rate limit hit: {error_msg}")
            raise