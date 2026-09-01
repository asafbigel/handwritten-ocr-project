# 🧮 Math-Mind Hybrid Grader

> An automated pipeline designed to evaluate handwritten math exams and worksheets using a **Hybrid AI Architecture**: local edge-processing for image anonymization (Privacy-First) combined with cloud-based Vision/LLM models for pedagogical evaluation.

---

## ✨ Core Features (Phase 1 MVP)

* **🛡️ Privacy-First (Zero PII Leakage):** No Personally Identifiable Information (PII) leaves the local machine. The system uses a lightweight local UI (`cv2.selectROI`) allowing the teacher to dynamically mask the student's name before any external API calls are made.
* **👁️ Human-in-the-Loop Verification:** After anonymization, the system presents the masked image to the teacher for visual confirmation, ensuring the student's identity is fully protected.
* **🧠 AI Self-Solving Engine:** Powered by Google's Gemini Vision model (configured via `GEMINI_MODEL`), the system independently solves the math questions and compares its solution against the student's handwritten answer. No teacher-supplied answer key is required.
* **🏗️ Strict Schema Enforcement:** Guarantees structured JSON outputs using Pydantic, enforcing a strict mapping of: `Question -> Student Answer -> Correct Answer -> Readability -> Grade`.
* **🧩 Decoupled Architecture:** Built with SOLID principles, utilizing the Strategy and Dependency Injection patterns. The core logic is completely agnostic to specific AI vendors or local UI implementations.

---

## ⚙️ System Requirements

* **Python:** `>= 3.10`
* **Package Manager:** `uv`

---

## 🚀 Installation & Setup

1. **Clone the repository and navigate to the root directory:**
```bash
git clone https://github.com/asafbigel/handwritten-ocr-project
cd handwritten-ocr-project
```

2. **Install dependencies and create the virtual environment using `uv`:**
```bash
uv sync
```

3. **Configure Environment Variables:**
Create a `.env` file in the root directory based on the `.env.example` structure. You must provide your Google Gemini API key:
```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3-flash-preview
INPUT_DIR=INPUT_DIR_PATH
OUTPUT_DIR=OUTPUT_DIR_PATH
REPORT_FORMAT=json
```

Optional overrides supported by the app:
- `GEMINI_MODEL`: Model name (defaults to `gemini-2.5-pro` if omitted)
- `INPUT_DIR`: Default input directory (default: `input`)
- `OUTPUT_DIR`: Default output directory (default: `output`)

---

## 💻 Usage

The system is operated via a Typer-based Command Line Interface (CLI). 

To run the full pipeline on a single exam image:

```bash
uv run math-mind path/to/exam_image.jpg
```

For example:
```bash
uv run math-mind data/images/A.jpg
```

## 🔄 Execution Flow Breakdown:
1. **Interactive Anonymization:** An OpenCV window will open displaying the exam. Click and drag your mouse to draw a bounding box over the student's name/details. Press `SPACE` or `ENTER` to confirm the crop.
2. **Visual Verification:** A new window will display the anonymized image (with the selected region blacked out). The terminal will prompt you to approve (Y/N) the anonymization.
3. **AI Evaluation:** Once approved, the image is sent to the Gemini Engine.
4. **Grading Report Output:** The CLI outputs the structured evaluation per question (`Question`, `Student Answer`, `Correct Answer`, `Readability`, `Grade`) directly to the log/console.

---

## 🏗️ Architecture Pipeline

The data flow is managed by the `GradingOrchestrator`, which passes a mutable `ExamContext` object through a distinct set of abstract interfaces:

| Step | Interface | Phase 1 Implementation | Responsibility |
| --- | --- | --- | --- |
| **1** | N/A | `ExamContext` | Loads the image into memory and initializes state tracking. |
| **2** | `Anonymizer` | `DynamicRoiAnonymizer` | Prompts the user to select an ROI and blacks it out. |
| **3** | `Verifier` | `CliVisualVerifier` | Displays the anonymized result and awaits human approval. |
| **4** | `GradingEngine` | `GeminiGradingEngine` | Communicates with the LLM API, enforces Pydantic schemas, and applies retry handling. |
| **5** | `Reporter` | *(In Progress)* | Will generate CSV/JSON batch reports. |

---

## 🗺️ Future Roadmap
* **Phase 2:** Image Deskewing, Alignment, and Visual Sorting.
* **Phase 3:** Secure User Authentication and Local Edge OCR for student name matching.
* **Phase 4:** Multi-Subject Support (English, Sciences) with teacher-supplied answer keys.
* **Phase 5:** Full Web GUI (FastAPI + React) and Mobile Application.