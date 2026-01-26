# CV Project Progress Tracker - 2026 Status Update

## 🎯 Current Project Status
* **Current Phase:** Phase 3: The Engine
* **Current Week:** Week 08: Digit Segmentation (In Progress)
* **Active Branch:** `feature/w08-digit-segmentation`
* **Latest Audit Yield:** **94% Average Recall** (100% match on 15/23 images)

---

## Phase 1: Foundations (Completed)
- [x] **Week 1: Python Data Stack & Regression** (Completed: Nov 28)
- [x] **Week 2: MNIST CNN built from scratch** (Completed: Dec 05)

---

## Phase 2: Computer Vision (Completed)
- [x] **Week 3: OpenCV Preprocessing Script** (Completed: Dec 12)
    * *Deliverable:* `src/preprocessing.py`
- [x] **Week 4: Geometry & Perspective Transform** (Completed: Dec 19)
    * *Status:* Completed via Fast Track.
- [x] **Week 5: Data Collection & Labeling** (Completed: Dec 31)
    * *Deliverable:* 23 high-quality labeled images.
    * *Note:* Dataset validated as sufficient for stable inference.

---

## Phase 3: The Engine (In Progress)
- [x] **Week 6: Train YOLOv8 Model** (Completed: Dec 31)
    * *Optimization:* Disabled Mosaic and Mixup to ensure training-inference parity.
    * *Parameters:* 100 total epochs, `imgsz=640`.
    * *Deliverable:* `best.pt` (no_mosaic version).

- [x] **Week 7: Inference & Audit Pipeline** (Completed: Jan 02)
    * *Status:* **SUCCESS - Ahead of Schedule.**
    * *Deliverables:* * `src/inference.py`: Extraction with $50px$ safe-padding.
        * `src/audit_model.py`: English-documented regression tool.
    * *Audit:* Verified 94% recall across the dataset.

- [/] **Week 8: Digit Segmentation** (Due: Jan 16)
    * *Goal:* Extract individual digits from the exercise crops.
    * *Tech:* OpenCV (Otsu Thresholding, Contours, Box Merging).
    * *Logic:* $Area > Min\_Area\_Threshold$ for noise filtering.

---

## Phase 4: Recognition & Production (Future)
- [ ] **Week 9: Character Recognition / OCR** (Due: Jan 23)
- [ ] **Week 10: Logic & Validation Layer** (Due: Jan 30)
- [ ] **Week 11: FastAPI Implementation** (Due: Feb 06)
- [ ] **Week 12: Dockerization** (Due: Feb 13)
- [ ] **Week 13: GitHub Polish & README** (Due: Feb 20)
- [ ] **Week 14: Final Buffer** (Due: Feb 27)

---

## 📝 Technical Notes & Risks
* **Padding:** Increased to $50px$ to prevent character cutoff during segmentation.
* **Confidence:** Set to $0.3$ to eliminate low-probability false positives.
* **Risk:** Small dataset (23 images) is a potential bottleneck for general OCR.