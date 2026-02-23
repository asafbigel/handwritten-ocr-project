import logging
from pathlib import Path

import cv2
import numpy as np

from ..interfaces.anonymizer import Anonymizer
from ..interfaces.grading_engine import GradingEngine
from ..interfaces.image_processor import ImageProcessor
from ..interfaces.reporter import Reporter
from ..interfaces.verifier import Verifier
from ..models.context import ExamContext, ExamStatus
from ..models.report import BatchResult, ExamReport
from ..utils.cleanup import TempFileManager

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"})


class GradingOrchestrator:
    """
    Pipeline hub — wires together all processing stages via Dependency
    Injection.  A fresh instance is created per folder so each folder can
    receive its own ``Anonymizer`` (per-folder crop region).
    """

    def __init__(
        self,
        anonymizer: Anonymizer,
        engine: GradingEngine,
        verifier: Verifier,
        reporters: list[Reporter],
        preprocessors: list[ImageProcessor] | None = None,
    ) -> None:
        self.anonymizer = anonymizer
        self.engine = engine
        self.verifier = verifier
        self.reporters = reporters
        self.preprocessors = preprocessors or []

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def process_folder(self, folder: Path, output_dir: Path) -> BatchResult:
        """Grade every exam image in *folder* and write reports to *output_dir*."""
        images = sorted(
            p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS
        )
        batch = BatchResult(folder=folder, total=len(images))

        with TempFileManager():
            for img_path in images:
                ctx = self._load(img_path)
                ctx = self._preprocess(ctx)
                ctx = self._anonymize(ctx)
                ctx = self._verify(ctx)
                ctx = self._grade(ctx)

                report = ExamReport(
                    exam_id=img_path.stem,
                    image_path=img_path,
                    grading_result=ctx.grading_result,
                    status=ctx.status.value,
                    errors=ctx.errors,
                )
                batch.reports.append(report)

                if ctx.status == ExamStatus.GRADED:
                    batch.graded += 1
                else:
                    batch.failed += 1

        for reporter in self.reporters:
            try:
                reporter.generate(batch, output_dir)
            except Exception as exc:
                logger.error("Reporter %s failed: %s", type(reporter).__name__, exc)

        return batch

    # ------------------------------------------------------------------
    # Pipeline stages
    # ------------------------------------------------------------------

    def _load(self, path: Path) -> ExamContext:
        img = cv2.imread(str(path))
        if img is None:
            ctx = ExamContext(
                image_path=path,
                original_image=np.zeros((1, 1, 3), dtype=np.uint8),
            )
            ctx.status = ExamStatus.FAILED
            ctx.errors.append(f"Could not read image: {path}")
            return ctx
        return ExamContext(image_path=path, original_image=img)

    def _preprocess(self, ctx: ExamContext) -> ExamContext:
        if ctx.status == ExamStatus.FAILED:
            return ctx
        try:
            for proc in self.preprocessors:
                ctx = proc.process(ctx)
        except Exception as exc:
            ctx.status = ExamStatus.FAILED
            ctx.errors.append(f"Preprocessing failed: {exc}")
        return ctx

    def _anonymize(self, ctx: ExamContext) -> ExamContext:
        if ctx.status == ExamStatus.FAILED:
            return ctx
        try:
            ctx.anonymized_image = self.anonymizer.anonymize(ctx.original_image)
            ctx.status = ExamStatus.ANONYMIZED
        except Exception as exc:
            ctx.status = ExamStatus.FAILED
            ctx.errors.append(f"Anonymisation failed: {exc}")
        return ctx

    def _verify(self, ctx: ExamContext) -> ExamContext:
        if ctx.status == ExamStatus.FAILED:
            return ctx
        try:
            approved = self.verifier.verify(
                ctx.original_image,
                ctx.anonymized_image,  # type: ignore[arg-type]
                ctx.image_path.stem,
            )
            if approved:
                ctx.anonymization_verified = True
                ctx.status = ExamStatus.VERIFIED
            else:
                ctx.status = ExamStatus.FAILED
                ctx.errors.append("Teacher rejected anonymisation")
        except Exception as exc:
            ctx.status = ExamStatus.FAILED
            ctx.errors.append(f"Verification failed: {exc}")
        return ctx

    def _grade(self, ctx: ExamContext) -> ExamContext:
        if ctx.status == ExamStatus.FAILED:
            return ctx
        try:
            ctx.grading_result = self.engine.grade(
                ctx.anonymized_image  # type: ignore[arg-type]
            )
            ctx.status = ExamStatus.GRADED
        except Exception as exc:
            ctx.status = ExamStatus.FAILED
            ctx.errors.append(f"Grading failed: {exc}")
        return ctx
