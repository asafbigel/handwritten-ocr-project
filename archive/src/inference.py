import cv2
import numpy as np
import os
from ultralytics import YOLO
from pathlib import Path

class ExerciseExtractor:
    """
    Handles the detection of mathematical exercises in images and 
    extracts them into individual image files for further processing.
    """
    
    def __init__(self, model_path, output_dir="temp_crops"):
        """
        Initializes the extractor with a trained YOLO model.
        
        Args:
            model_path (str): Path to the .pt weight file.
            output_dir (str): Directory where cropped exercises will be saved.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
            
        self.model = YOLO(model_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _safe_crop(self, image, box, padding=50):
        """
        Crops an image based on a bounding box with safety margins.
        
        Uses np.clip to ensure that adding padding doesn't result in 
        out-of-bounds coordinates, which would cause NumPy slicing errors.
        
        Args:
            image (np.ndarray): The source image matrix.
            box (torch.Tensor): Bounding box coordinates from YOLO (xyxy).
            padding (int): Pixels to add around the detected box.
            
        Returns:
            np.ndarray: The cropped image segment.
        """
        h, w = image.shape[:2]
        
        # Convert GPU tensor to CPU numpy array and cast to integers
        x1, y1, x2, y2 = box.cpu().numpy().astype(int)

        # Apply padding and clip to image boundaries
        x1_pad = np.clip(x1 - padding, 0, w)
        y1_pad = np.clip(y1 - padding, 0, h)
        x2_pad = np.clip(x2 + padding, 0, w)
        y2_pad = np.clip(y2 + padding, 0, h)

        return image[y1_pad:y2_pad, x1_pad:x2_pad]

    def process_image(self, image_path, confidence=0.6):
        """
        Runs inference on an image and saves each detected exercise as a separate file.
        
        Args:
            image_path (str): Path to the input image.
            confidence (float): Minimum confidence threshold for detection.
            
        Returns:
            list: Paths to the saved crop files.
        """
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"Error: Could not read image {image_path}")
            return []

        # Run YOLOv8 inference
        results = self.model.predict(source=img, conf=confidence, verbose=False)
        
        print(f"DEBUG: Found {len(results[0].boxes)} total potential boxes.")
        for i, box in enumerate(results[0].boxes):
            conf = float(box.conf[0])
            print(f"Box {i}: Confidence = {conf:.4f}")
        
        crop_paths = []
        image_stem = Path(image_path).stem 

        # Results[0] contains the detection for the current image
        for i, box in enumerate(results[0].boxes.xyxy):
            crop = self._safe_crop(img, box)
            
            # Construct a unique filename for each exercise
            output_filename = f"{image_stem}_ex_{i}.jpg"
            output_path = self.output_dir / output_filename
            
            # Save to disk
            cv2.imwrite(str(output_path), crop)
            crop_paths.append(str(output_path))
            
        print(f"Successfully extracted {len(crop_paths)} crops to {self.output_dir}")
        return crop_paths

if __name__ == "__main__":
    # Internal validation logic
    FILE = Path(__file__).resolve()
    ROOT = FILE.parent.parent
    MODEL_WEIGHTS = ROOT / "runs" / "detect" / "handwritten_no_mosaic" / "weights" / "best.pt"
    TEST_IMAGE = ROOT / "data" / "dataset" / "images" / "20251207_211908.jpg"
    print(f"Project Root: {ROOT}")
    print(f"Loading model from: {MODEL_WEIGHTS}")
    print(f'Try processing image: {TEST_IMAGE}')
    
    try:
        extractor = ExerciseExtractor(MODEL_WEIGHTS)
        extractor.process_image(TEST_IMAGE, confidence=0.3)
    except Exception as e:
        print(f"Pipeline execution failed: {e}")