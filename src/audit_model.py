import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

class ModelAuditor:
    def __init__(self, model_path, data_root):
        """
        Initializes the ModelAuditor with model weights and dataset paths.
        """
        self.model = YOLO(model_path)
        self.data_root = Path(data_root)
        self.img_dir = self.data_root / "images"
        self.lbl_dir = self.data_root / "labels"

    def load_gt_boxes(self, label_path, img_w, img_h):
        """
        Loads original Ground Truth labels from TXT files and converts 
        normalized YOLO coordinates to absolute pixel coordinates.
        """
        boxes = []
        if not label_path.exists():
            return boxes
        with open(label_path, 'r') as f:
            for line in f.readlines():
                # YOLO format: class x_center y_center width height (normalized)
                _, x, y, w, h = map(float, line.split())
                
                # Convert normalized coordinates to absolute pixels
                x1 = int((x - w/2) * img_w)
                y1 = int((y - h/2) * img_h)
                x2 = int((x + w/2) * img_w)
                y2 = int((y + h/2) * img_h)
                boxes.append([x1, y1, x2, y2])
        return boxes

    def run_audit(self, conf_threshold=0.3):
        """
        Iterates through the image directory, runs inference, and compares 
        the number of detected boxes against Ground Truth labels.
        """
        print(f"Searching for images in: {self.img_dir.absolute()}")

        # Robust search: handling case-sensitivity by using sets to avoid duplicates
        images = list(set(list(self.img_dir.glob("*.jpg")) + list(self.img_dir.glob("*.JPG"))))
        
        if not images:
            print(f"Error: No images found!")
            return

        print(f"Starting Audit on {len(images)} images...\n")
        print(f"{'Image':<30} | {'GT':<5} | {'Found':<5} | {'Match %'}")
        print("-" * 60)

        for img_path in images:
            img = cv2.imread(str(img_path))
            if img is None:
                continue
                
            h, w, _ = img.shape
            
            # 1. Load Ground Truth boxes
            label_path = self.lbl_dir / (img_path.stem + ".txt")
            gt_boxes = self.load_gt_boxes(label_path, w, h)
            
            # 2. Run model inference
            results = self.model.predict(source=img, conf=conf_threshold, imgsz=640, verbose=False)
            pred_boxes = results[0].boxes.xyxy.cpu().numpy().astype(int).tolist()

            # 3. Basic quantitative comparison
            gt_count = len(gt_boxes)
            pred_count = len(pred_boxes)
            
            # Calculate match rate based on counts
            match_rate = (min(pred_count, gt_count) / gt_count * 100) if gt_count > 0 else 0
            
            print(f"{img_path.name:<30} | {gt_count:<5} | {pred_count:<5} | {match_rate:.1f}%")

if __name__ == "__main__":
    # Define project paths
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    MODEL = PROJECT_ROOT / "runs" / "detect" / "handwritten_no_mosaic" / "weights" / "best.pt"
    DATA = PROJECT_ROOT / "data" / "dataset"
    
    # Run the audit process
    auditor = ModelAuditor(MODEL, DATA)
    auditor.run_audit()