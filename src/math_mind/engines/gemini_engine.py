import cv2
import numpy as np
from google import genai
from google.genai import types

from ..interfaces.grading_engine import GradingEngine
from ..models.grading import GradingResult
from ..utils.rate_limiter import RateLimiter
from ..utils.retry import with_retry

_GRADING_PROMPT = """\
You are a math teacher grading a handwritten student exam.

For EACH question visible in the image:
1. Transcribe the question text.
2. Transcribe the student's handwritten answer exactly as written.
3. Solve the question yourself to obtain the correct answer.
4. Rate the readability of the student's handwriting:
   - CLEAR   — fully legible
   - PARTIAL — partially legible
   - UNCLEAR — illegible
5. Assign a numeric grade (points earned for this question, ≥ 0).
6. Add any short notes (optional).

Then produce:
- total_score: sum of all question grades.
- max_score:   maximum achievable total (infer from question structure).
- overall_notes: optional summary.

Return ONLY a JSON object that matches the required schema — no prose.
"""


class GeminiGradingEngine(GradingEngine):
    """
    Uses the google-genai SDK to grade exam images via structured output.

    Rate limiting is *proactive* (blocks before sending) and retry is
    *reactive* (exponential backoff on transient / 429 errors).
    """

    def __init__(self, api_key: str, model: str, rate_limiter: RateLimiter) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._rate_limiter = rate_limiter

        # Wrap the inner implementation with retry logic at construction time
        # so the public `grade` method stays clean.
        self._grade_impl = with_retry(
            max_attempts=4,
            base_delay=2.0,
            backoff=2.0,
        )(self._grade_impl)

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------

    def grade(self, image: np.ndarray) -> GradingResult:
        return self._grade_impl(image)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _grade_impl(self, image: np.ndarray) -> GradingResult:
        self._rate_limiter.acquire()

        _, buffer = cv2.imencode(".jpg", image)
        image_bytes = buffer.tobytes()

        response = self._client.models.generate_content(
            model=self._model,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                _GRADING_PROMPT,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GradingResult,
            ),
        )
        return GradingResult.model_validate_json(response.text)
