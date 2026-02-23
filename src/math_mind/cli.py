"""
Composition Root — the only module that knows about concrete classes.

All dependency wiring happens here; everything else depends on ABCs only.

Per-folder crop region
──────────────────────
The CLI iterates over subfolders in INPUT_DIR.  For each folder it calls
``settings.get_crop_region(folder.name)`` to resolve the correct rectangle
to anonymise, then constructs a fresh ``CropAnonymizer`` and
``GradingOrchestrator`` for that folder.

This means:
  • ``GeminiGradingEngine``  — created once, shared across all folders
  • ``Reporters``            — created once, shared across all folders
  • ``CropAnonymizer``       — created per folder (different rect per class)
  • ``GradingOrchestrator``  — created per folder (receives folder's anonymizer)
"""

import logging
from pathlib import Path
from typing import Annotated

import typer

from .anonymization.crop_anonymizer import CropAnonymizer
from .config import AppSettings
from .engines.gemini_engine import GeminiGradingEngine
from .pipeline.orchestrator import IMAGE_EXTENSIONS, GradingOrchestrator
from .reporting.csv_reporter import CsvReporter
from .reporting.json_reporter import JsonReporter
from .utils.rate_limiter import RateLimiter
from .verification.cli_verifier import CliVisualVerifier

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger(__name__)

app = typer.Typer(
    name="math-mind",
    help="AI-powered handwritten math exam grader.",
    add_completion=False,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_reporters(formats: list[str]) -> list:
    reporters = []
    if "csv" in formats:
        reporters.append(CsvReporter())
    if "json" in formats:
        reporters.append(JsonReporter())
    return reporters


def _resolve_folders(input_dir: Path) -> list[Path]:
    """Return subfolders, or [input_dir] itself if there are none."""
    subfolders = [p for p in sorted(input_dir.iterdir()) if p.is_dir()]
    return subfolders if subfolders else [input_dir]


def _warn_no_region(folder_name: str) -> None:
    typer.echo(
        f"  [Warning] No crop_region configured for folder '{folder_name}'. "
        "Using a zero-size region (anonymisation step is a no-op). "
        "Set CROP_REGIONS or DEFAULT_CROP_REGION in your .env file.",
        err=True,
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def grade(
    input_dir: Annotated[
        Path | None,
        typer.Argument(help="Folder containing exam images or subfolders."),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Where to write reports."),
    ] = None,
) -> None:
    """
    Grade all exams in INPUT_DIR.

    Each direct subfolder is treated as a separate exam class and may
    have its own anonymisation crop region (configured via CROP_REGIONS
    in your .env file).
    """
    settings = AppSettings()  # type: ignore[call-arg]
    effective_input = input_dir or settings.input_dir
    effective_output = output_dir or settings.output_dir

    if not effective_input.exists():
        typer.echo(f"Error: '{effective_input}' does not exist.", err=True)
        raise typer.Exit(1)

    rate_limiter = RateLimiter(rpm=settings.rpm_limit, rpd=settings.rpd_limit)
    engine = GeminiGradingEngine(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        rate_limiter=rate_limiter,
    )
    verifier = CliVisualVerifier()
    reporters = _build_reporters(settings.report_formats)
    folders = _resolve_folders(effective_input)

    for folder in folders:
        typer.echo(f"\n== Processing folder: {folder.name} ==")

        region = settings.get_crop_region(folder.name)
        if region is None:
            _warn_no_region(folder.name)
            region = (0, 0, 0, 0)  # no-op: zero-size fill

        anonymizer = CropAnonymizer(region)
        orchestrator = GradingOrchestrator(
            anonymizer=anonymizer,
            engine=engine,
            verifier=verifier,
            reporters=reporters,
        )
        result = orchestrator.process_folder(folder, effective_output)
        typer.echo(
            f"   Graded: {result.graded}/{result.total}  |  Failed: {result.failed}"
        )


@app.command(name="verify-only")
def verify_only(
    input_dir: Annotated[
        Path | None,
        typer.Argument(help="Folder containing exam images or subfolders."),
    ] = None,
) -> None:
    """
    Run anonymisation + teacher verification without grading.

    Useful for previewing the crop region before committing to a full run.
    """
    settings = AppSettings()  # type: ignore[call-arg]
    effective_input = input_dir or settings.input_dir

    if not effective_input.exists():
        typer.echo(f"Error: '{effective_input}' does not exist.", err=True)
        raise typer.Exit(1)

    import cv2

    folders = _resolve_folders(effective_input)
    verifier = CliVisualVerifier()

    for folder in folders:
        region = settings.get_crop_region(folder.name)
        if region is None:
            _warn_no_region(folder.name)
            continue

        anonymizer = CropAnonymizer(region)
        typer.echo(f"\n== Verifying folder: {folder.name} ==")

        images = sorted(
            p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS
        )
        for img_path in images:
            img = cv2.imread(str(img_path))
            if img is None:
                typer.echo(f"  Could not read: {img_path.name}")
                continue
            anon = anonymizer.anonymize(img)
            approved = verifier.verify(img, anon, img_path.stem)
            typer.echo(f"  {img_path.name}: {'APPROVED' if approved else 'REJECTED'}")
