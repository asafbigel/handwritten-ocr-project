# Plan: Math-Mind Phase 1 MVP Architecture

The system is built from scratch in `src/math_mind/` using **5 abstract interfaces** (Strategy Pattern) wired together by a **GradingOrchestrator** (Dependency Injection) that passes a mutable **ExamContext** through a processing chain (Pipeline Pattern). Phase 1 delivers image ingestion, static crop anonymization, teacher visual verification, Gemini-powered self-solving math grading with Pydantic schema enforcement, rate-limit resilience, and CSV/JSON reporting.

---

## Package Structure

```
handwritten-ocr-project/
├── .env.example
├── pyproject.toml
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_anonymizer.py
│   ├── test_orchestrator.py
│   └── test_reporters.py
└── src/
    └── math_mind/
        ├── __init__.py
        ├── __main__.py              # python -m math_mind
        ├── cli.py                   # Typer app (grade, verify-only)
        ├── config.py                # AppSettings via pydantic-settings
        ├── models/
        │   ├── context.py           # ExamContext dataclass, ExamStatus enum
        │   ├── grading.py           # QuestionResult, GradingResult, Readability
        │   └── report.py            # ExamReport, BatchResult
        ├── interfaces/
        │   ├── anonymizer.py        # Anonymizer ABC
        │   ├── grading_engine.py    # GradingEngine ABC
        │   ├── reporter.py          # Reporter ABC
        │   ├── verifier.py          # Verifier ABC
        │   └── image_processor.py   # ImageProcessor ABC (Phase 2 placeholder)
        ├── anonymization/
        │   └── crop_anonymizer.py   # CropAnonymizer — static rect fill
        ├── engines/
        │   └── gemini_engine.py     # GeminiGradingEngine — google-genai SDK
        ├── pipeline/
        │   └── orchestrator.py      # GradingOrchestrator — DI hub
        ├── reporting/
        │   ├── csv_reporter.py
        │   └── json_reporter.py
        ├── verification/
        │   └── cli_verifier.py      # cv2.imshow + Y/N prompt
        └── utils/
            ├── rate_limiter.py      # Sliding-window RPM/RPD tracker
            ├── retry.py             # Exponential backoff decorator
            └── cleanup.py           # TempFileManager context manager
```

---

## 5 Abstract Interfaces

| Interface | Method Signature | Phase 1 Implementation |
|---|---|---|
| **`Anonymizer`** | `anonymize(image: ndarray) -> ndarray` | `DynamicRoiAnonymizer` — DynamicRoiAnonymizer — prompts user to select ROI via UI and crop region |
| **`GradingEngine`** | `grade(image: ndarray) -> GradingResult` | `GeminiGradingEngine` — google-genai structured output, rate-limited |
| **`Reporter`** | `generate(result: BatchResult, output_dir: Path) -> Path` | `CsvReporter`, `JsonReporter` |
| **`Verifier`** | `verify(original: ndarray, anonymized: ndarray, name: str) -> bool` | `CliVisualVerifier` — shows image, asks teacher Y/N |
| **`ImageProcessor`** | `process(context: ExamContext) -> ExamContext` | *None yet* — placeholder for Phase 2 deskewing/enhancement |

---

## Key Domain Models

**`ExamContext`** (dataclass — mutable pipeline object, holds `np.ndarray`):
- `image_path`, `original_image`, `anonymized_image`, `anonymization_verified`, `grading_result`, `status` (PENDING → ANONYMIZED → VERIFIED → GRADED | FAILED), `errors`

**`GradingResult`** / **`QuestionResult`** (Pydantic — FR1.5 strict schema):
- Question → Student Answer → Correct Answer (AI self-solved) → Readability (CLEAR/PARTIAL/UNCLEAR) → Grade → Notes

**`AppSettings`** (pydantic-settings, loads from `.env`):
- `gemini_api_key`, `gemini_model`, `input_dir`, `output_dir`, `report_formats`, `rpm_limit`, `rpd_limit`

---

## Orchestrator Pipeline Flow

`GradingOrchestrator` receives all dependencies via constructor (DI). For each image:

1. **Load** → create `ExamContext` with loaded image
2. **Preprocess** → run each `ImageProcessor.process()` *(empty list in Phase 1)*
3. **Anonymize** → `Anonymizer.anonymize()` → status = ANONYMIZED
4. **Verify** → `Verifier.verify()` → teacher approves or rejects → status = VERIFIED | FAILED
5. **Grade** → `GradingEngine.grade()` → status = GRADED
6. **Aggregate** → collect into `BatchResult`, call each `Reporter.generate()`
7. **Cleanup** → `TempFileManager` deletes intermediate files (NFR1)

Any exception at steps 2-5 → status = FAILED, error logged, batch continues.

---

## Rate Limiting & Retry (NFR3, NFR4)

- **`RateLimiter`** — proactive sliding-window: blocks with status message before sending if RPM/RPD exhausted
- **`with_retry` decorator** — reactive: catches 429 (`ResourceExhausted`) + network errors, exponential backoff
- Both are injected into `GeminiGradingEngine`

---

## Implementation Steps

### Phase A: Project Scaffolding
1. Delete empty `scr/`, create full `src/math_mind/` directory tree with `__init__.py` files
2. Create `pyproject.toml` (uv, deps: `google-genai`, `pydantic`, `pydantic-settings`, `opencv-python-headless`, `typer`, `numpy`; dev: `pytest`, `pytest-cov`; script entry: `math-mind = "math_mind.cli:app"`)
3. Create `.env.example`, update `.gitignore`

### Phase B: Models & Interfaces *(all parallel)*
4. Implement `models/grading.py`, `models/report.py`, `models/context.py`
5. Implement `config.py` (AppSettings)
6. Implement all 5 ABCs in `interfaces/`

### Phase C: Core Implementations *(parallel where deps allow)*
7. `utils/rate_limiter.py`, `utils/retry.py`, `utils/cleanup.py`
8. `anonymization/crop_anonymizer.py` — *depends on Anonymizer ABC*
9. `verification/cli_verifier.py` — *depends on Verifier ABC*
10. `engines/gemini_engine.py` — *depends on GradingEngine ABC + models + rate_limiter*
11. `reporting/csv_reporter.py` + `json_reporter.py` — *depends on Reporter ABC + models*

### Phase D: Pipeline & CLI
12. `pipeline/orchestrator.py` — *depends on all Phase C*
13. `cli.py` (composition root, wires DI) + `__main__.py` — *depends on step 12*

### Phase E: Testing
14. `conftest.py` (fixtures: sample image, mock engine, auto-approve verifier)
15. `test_models.py`, `test_anonymizer.py`, `test_orchestrator.py`, `test_reporters.py` — *parallel*

---

## Relevant Files

- **Create:** `pyproject.toml`, `.env.example`, `src/math_mind/**`, `tests/**`
- **Modify:** `.gitignore` — add `.env`, `output/`, `__pycache__/`
- **Delete:** `scr/` (empty typo directory)
- **Reference (read-only):** `archive/src/inference.py` (`_safe_crop` logic), `archive/src/preprocessing.py` (OpenCV chains), `archive/main.py` (pipeline pattern)

---

## Verification
1. `uv run ruff check src/ tests/` — lint clean
2. `uv run pytest tests/ -v` — all green
3. `uv run python -c "from math_mind.interfaces import Anonymizer, GradingEngine, Reporter, Verifier, ImageProcessor"` — import succeeds
4. `uv run math-mind --help` — shows `grade` and `verify-only` commands
5. Manual E2E: `uv run math-mind grade ./test_images/` with real Gemini key against existing test images at root
6. Confirm no temp files remain after pipeline completes

---

## Decisions
- **`ExamContext` = dataclass** (not Pydantic) — holds `np.ndarray`, must be mutable
- **`GradingResult` = Pydantic** — enforces FR1.5 strict schema, enables Gemini structured output
- **`ImageProcessor` defined but empty** — satisfies Open-Closed for Phase 2
- **`cli.py` is the composition root** — only place that knows concrete classes and wires DI
- **Rate limiter is proactive** (blocks before sending) + reactive fallback (retry after 429)

## Scope
- **In:** Full Phase 1 MVP (FR1.1–FR1.6, NFR1–NFR4)
- **Out:** Phases 2–5 (deskewing, clustering, auth, web UI, mobile). Only the `ImageProcessor` interface serves as a forward placeholder.
- **Out:** Archive code is not migrated — reference only