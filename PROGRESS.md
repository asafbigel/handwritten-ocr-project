# Math-Mind Hybrid Grader - Progress Tracker
**MVP Hard Deadline: March 15, 2026**

## 🎯 Current Milestone: MVP: PENDING FIXES ⚠️

### ✅ DONE (Phase 0 & Phase 1)
- [x] Project scaffolding with `uv` and `pyproject.toml`.
- [x] Architecture design: Interfaces established (`src/math_mind/interfaces/anonymizer.py`).
- [x] Component: `DynamicRoiAnonymizer` implemented (Using `cv2.selectROI`).
- [x] Testing: `test_anonymizer.py` completed with 100% coverage. `apply_mask` is a strict Pure Function. 
- [x] Security: No PII leakage in the anonymization process.

### ✅ DONE: (Phase 1.5)
- [x] Define the `Verifier` interface (`src/math_mind/interfaces/verifier.py`).
- [x] Write a Test Plan for the verification logic (abstracting the keypress).
- [x] Implement `CliVisualVerifier` using `cv2.imshow` and `cv2.waitKey`.
- [x] Pass `pytest` coverage for Phase 1.5.

### ✅ DONE: Phase 2 & 3 - AI Integration & Structured Data
- [x] Define `GradingEngine` interface.
- [x] Define Pydantic models for structured output (`GradingResult`, `QuestionResult`).
- [x] Implement `GeminiGradingEngine` (`google-genai` SDK, Gemini 2.5 Flash).
- [x] Integrate Pydantic schema with Gemini payload (Strict Structured Output).
- [x] Robust Error Mapping and Reactive Retry mechanism (`with_retry` decorator).

### ✅ DONE: Phase 4 - CLI & Orchestrator (Deadline: Mar 11, 2026)
- [x] Build `GradingOrchestrator` to chain: `Load` -> `Anonymize` -> `Verify` -> `Grade` -> `Report`.
- [x] Create `ExamContext` data structure to pass state safely between components.
- [x] Implement CLI interface using Typer (Typer-based CLI).
- [x] E2E Testing of the complete pipeline.

### 🚀 MVP RELEASE (Deadline: Mar 15, 2026)
- [x] Buffer for debugging, edge cases, and final manual validation.

### 🚧 Technical Debt & Missing Features (Audit Results)
- [ ] Implement directory batch ingestion in the Typer CLI (accept JPG/PNG folders, not only a single image path) (FR1.1).
- [ ] Add `Reporter` and `ImageProcessor` interfaces and wire them through dependency injection in the orchestrator (NFR2, ARCHITECTURE.md).
- [ ] Implement local CSV/JSON batch report generation with per-image outcomes and UNCLEAR flags (FR1.6).
- [ ] Refactor `GradingOrchestrator` into a resilient batch pipeline that continues on per-file failures instead of aborting execution (NFR3).
- [ ] Implement proactive Gemini quota management for per-minute, per-hour, per-day, and per-month limits with pause-and-resume behavior (NFR4).
- [ ] Integrate the rate-limiter into `GeminiGradingEngine` and remove dead/commented limiter code paths (NFR3, NFR4).
- [ ] Add cleanup management for intermediate artifacts with guaranteed post-run deletion hooks (NFR1, ARCHITECTURE.md).
- [ ] Create and commit `.env.example` documenting required runtime variables (e.g., `GEMINI_API_KEY`, `GEMINI_MODEL`) (NFR1, ARCHITECTURE.md).