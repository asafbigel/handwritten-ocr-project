# 📄 Product Requirements Document (PRD): Math-Mind Hybrid Grader

## 1. Executive Summary
**Math-Mind** is an automated pipeline designed to evaluate handwritten math exams and worksheets. The system leverages a **Hybrid AI Architecture**: local edge-processing for image anonymization (Privacy-First) combined with cloud-based Vision/LLM models for pedagogical evaluation. 

The system is fundamentally designed to be **future-proof**. By utilizing a decoupled, modular (Plug-and-Play) architecture, the core logic remains agnostic to the underlying UI, local databases, or specific AI vendors, allowing seamless integration of future technologies.

---

## 2. Core Objectives
1. **Privacy-First (Zero PII Leakage):** No Personally Identifiable Information (PII), such as student names, will ever leave the local machine or enterprise server. 
2. **Pedagogical Accuracy (Anti-Hallucination):** The system prioritizes grading integrity. It is strictly instructed to flag ambiguous handwriting as "UNCLEAR" (requiring Human-in-the-Loop review) rather than hallucinating or guessing a grade.
3. **Decoupled Architecture:** Business logic is strictly separated from presentation (UI). AI interfaces are vendor-agnostic, and the vision pipeline is modular to allow hot-swapping of algorithms.

---

## 3. User Personas
* **Teacher / Grader:** Uploads exam batches, defines grading rubrics, manually reviews flagged "UNCLEAR" answers, and exports final reports.
* **System Administrator:** Configures API keys, manages local student databases, and handles system environments.

---

## 4. Functional Requirements (FR)

The features are staggered into phases to prioritize the MVP deadline while mapping out the long-term vision.

### Phase 1: The Core MVP (Target Deadline: Mar 15, 2026)
* **FR1.1 Image Ingestion:** The system shall accept a local directory containing raw scanned images (JPG/PNG).
* **FR1.2 Basic Anonymization:** The system shall use OpenCV to mask the exam header (student name region) before any external API calls. The system will present a lightweight UI (e.g., cv2.selectROI) allowing the teacher to dynamically draw a bounding box around the student's name. The system will then black out this selected Region of Interest (ROI).
* **FR1.3 Anonymization Verification:** After anonymization, the system shall present each masked image to the teacher for visual confirmation that the student name has been fully removed before proceeding to the AI grading step.
* **FR1.4 AI Grading Engine (Self-Solving):** The system shall communicate with the `gemini` model via the `google-genai` SDK to evaluate the anonymized math exams. For math, the AI model **solves the questions independently** and compares its solution against the student's handwritten answer — no teacher-supplied answer key is required.
* **FR1.5 Strict Schema Enforcement:** The system shall enforce a strict JSON output schema using Pydantic (mapping: Question -> Student Answer -> Correct Answer -> Readability -> Grade).
* **FR1.6 Local Reporting:** The system shall generate a structured local report (CSV/JSON) summarizing the batch results, including per-image error details and UNCLEAR flags.

### Phase 2: Vision & Pipeline Enhancements
* **FR2.1 Deskewing & Alignment:** Implement corner detection and Warp Perspective to normalize skewed scans or mobile photos.
* **FR2.2 Visual Sorting (Clustering):** Group exams belonging to the same student based on visual similarity/image hashing without performing text-based OCR on the name.
* **FR2.3 Image Enhancement:** Apply local pre-processing filters (Binarization, Contrast Adjustment, Noise Reduction) to improve readability for the AI engine.

### Phase 3: Identity, Data & UX
* **FR3.1 User Authentication:** Implement secure login for educators (Session management).
* **FR3.2 Local Student Database:** Manage a local repository mapping student IDs to names (SQLite/JSON).
* **FR3.3 Advanced Edge Recognition:**
  * Match cropped name-regions against a predefined list of students.
  * Train and deploy a lightweight Local/Edge AI model to perform offline OCR on student names.
* **FR3.4 Dynamic Rubrics:** Provide an interface for teachers to assign specific point weights to individual questions dynamically.

### Phase 4: AI Expansion & Multi-Domain
* **FR4.1 Multi-Subject Support:** Expand grading capabilities to subjects beyond math (e.g., English, Sciences). For non-math subjects where the AI cannot independently derive the correct answer, the system shall accept a **teacher-supplied answer key** (JSON/YAML) mapping question numbers to correct answers and point values.
* **FR4.2 NLP & Syntax Grading:** Evaluate free-text answers for syntax, grammar, and spelling, assigning scores based on user-defined parameters.
* **FR4.3 Third-Party AI Integrations:** Implement alternative Engine adapters (e.g., OpenAI, GitHub Copilot SDK) to allow natural-language prompt-based grading definitions.

### Phase 5: Multi-Platform Ecosystem
* **FR5.1 GUI / Web Application:** Develop a comprehensive frontend (e.g., FastAPI + React, or Streamlit) decoupled from the backend core.
* **FR5.2 Mobile Application:** Develop a client-side mobile app to capture exams, perform on-device anonymization, and fetch immediate grades from the cloud.

---

## 5. Non-Functional Requirements (NFR)
* **NFR1 Security:** API keys must be managed strictly via environment variables (`.env`, excluded from version control via `.gitignore`). Original exam images are retained locally as the teacher's source of truth. Temporary/intermediate files (e.g., anonymized copies sent to the API) must be cleaned up after the pipeline execution completes.
* **NFR2 Extensibility (SOLID):** The system must adhere to the Open-Closed Principle. Adding a new AI model or a new image filter must only require implementing an existing Interface, requiring zero modifications to the core orchestrator.
* **NFR3 Reliability:** The system must implement robust Retry & Error Handling mechanisms to manage network timeouts, API rate limits, and unreadable files without crashing the batch process.
* **NFR4 Rate Limit Resilience (Gemini Free Tier):** The system currently relies on the Gemini free tier. It must detect and handle rate-limit responses at all granularities (per-minute, per-hour, per-day, per-month). When a limit is hit, the batch shall pause with a clear status message and automatically resume when the window resets, rather than failing the entire batch.

---

## 6. High-Level Architecture Scope
The system will implement the following Design Patterns:
* **Strategy Pattern:** For interchangeable AI grading engines and image processing algorithms.
* **Dependency Injection (DI):** The main Orchestrator will accept its dependencies (Processors, Engines, Storage) during initialization to facilitate unit testing and modularity.
* **Pipeline Pattern:** Passing a mutable `ExamContext` object through a chain of processing filters.

---

## 7. Document Scope
This PRD provides **detailed requirements for Phase 1 (MVP)** and high-level summaries for Phases 2–5 as roadmap context. Each subsequent phase will receive its own dedicated, detailed PRD document when development for that phase begins.