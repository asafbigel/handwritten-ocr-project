# Math-Mind Hybrid Grader - Progress Tracker
**MVP Hard Deadline: March 15, 2026**

## 🎯 Current Milestone: Phase 1.5 - The Verifier (Human-in-the-Loop)

### ✅ DONE (Phase 0 & Phase 1)
- [x] Project scaffolding with `uv` and `pyproject.toml`.
- [x] Architecture design: Interfaces established (`src/math_mind/interfaces/anonymizer.py`).
- [x] Component: `DynamicRoiAnonymizer` implemented (Using `cv2.selectROI`).
- [x] Testing: `test_anonymizer.py` completed with 100% coverage. `apply_mask` is a strict Pure Function. 
- [x] Security: No PII leakage in the anonymization process.

### 🚧 NEXT UP: Phase 1.5 (Deadline: Feb 27, 2026)
- [ ] Define the `Verifier` interface (`src/math_mind/interfaces/verifier.py`).
- [ ] Write a Test Plan for the verification logic (abstracting the keypress).
- [ ] Implement `CliVisualVerifier` using `cv2.imshow` and `cv2.waitKey`.
- [ ] Pass `pytest` coverage for Phase 1.5.

### ⏳ PENDING: Phase 2 - AI Integration (Deadline: Mar 4, 2026)
- [ ] Define `AiVision` interface.
- [ ] Implement `GeminiClient` (`google-genai` SDK, Gemini 2.5 Flash).
- [ ] Test API integration with `unittest.mock`.

### ⏳ PENDING: Phase 3 - Structured Data (Deadline: Mar 7, 2026)
- [ ] Define Pydantic models for structured output (`GradingResult`).
- [ ] Integrate Pydantic schema with Gemini payload.

### ⏳ PENDING: Phase 4 - CLI & E2E (Deadline: Mar 11, 2026)
- [ ] Build the CLI Orchestrator (`src/math_mind/cli.py`) using `argparse` or `typer`.
- [ ] Connect Anonymizer -> Verifier -> GeminiClient.
- [ ] Write End-to-End (E2E) integration test.

### 🚀 MVP RELEASE (Deadline: Mar 15, 2026)
- [ ] Buffer for debugging, edge cases, and final manual validation.