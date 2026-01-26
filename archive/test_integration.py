import os
import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO
# מוודא שהפונקציה קיימת - אם הקוד הקודם לא בתיקייה הנכונה זה יכשל
from src.segmentation import segment_digits 

# --- CONFIGURATION ---
MODEL_PATH = r'models/ocr_model_v1.pt'
# שים לב: עדכנתי את הנתיב לנתיב יחסי סטנדרטי. תבדוק שזה תואם לתיקיות שלך!
IMAGES_DIR = r'data/dataset/images' 

def load_model():
    """
    Load model once. Return None if fails.
    """
    if os.path.exists(MODEL_PATH):
        print(f">> ✅ Loading model from: {MODEL_PATH}")
        return YOLO(MODEL_PATH)
    else:
        print(f">> ⚠️ Model not found at {MODEL_PATH}. Using Heuristic Fallback.")
        return None

def extract_crops_yolo(model, image):
    # verbose=False כדי לא להספים את הקונסול
    results = model(image, verbose=False) 
    
    crops = []
    h_img, w_img, _ = image.shape
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            
            # Safety Padding (לא לצאת מגבולות התמונה)
            pad = 10
            y1 = max(0, y1 - pad)
            y2 = min(h_img, y2 + pad)
            x1 = max(0, x1 - pad)
            x2 = min(w_img, x2 + pad)
            
            crop = image[y1:y2, x1:x2]
            crops.append((crop, y1)) 
            
    # Sort Top-to-Bottom
    crops.sort(key=lambda x: x[1])
    return [c[0] for c in crops]

def extract_crops_heuristic(image):
    # Fallback logic
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5))
    connected = cv2.dilate(thresh, kernel, iterations=2)
    contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    crops = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w * h > 1000 and w > 50: 
             crops.append((image[y:y+h, x:x+w], y))
             
    crops.sort(key=lambda x: x[1])
    return [c[0] for c in crops]

def process_and_display(filename, crops):
    if not crops:
        print(f"[{filename}] No exercises found.")
        return

    # Dynamic Layout
    cols = 3
    rows = (len(crops) // cols) + 1
    if len(crops) % cols != 0: rows += 1
    
    plt.figure(figsize=(15, 3 * rows))
    plt.suptitle(f"File: {filename}", fontsize=16)
    
    for i, crop in enumerate(crops):
        # --- WEEK 8 SEGMENTATION LOGIC ---
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY_INV, 15, 10)
        
        # שימוש בפונקציה מהמודול שיצרנו
        digit_boxes = segment_digits(binary, min_area=25)
        # ---------------------------------

        # Visualization
        debug_crop = crop.copy()
        for (x, y, w, h) in digit_boxes:
            cv2.rectangle(debug_crop, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
        plt.subplot(rows, cols, i+1)
        plt.imshow(cv2.cvtColor(debug_crop, cv2.COLOR_BGR2RGB))
        plt.title(f"Ex {i+1}: {len(digit_boxes)} Digits")
        plt.axis('off')
        
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # 1. Validation check
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ Error: Directory not found: {os.path.abspath(IMAGES_DIR)}")
        print("   -> Check if your images are in 'data/dataset/images' or 'data/raw'")
        exit(1)

    # 2. Load Model ONCE (Outside the loop)
    model = load_model()

    # 3. Iterate over images
    files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f">> Found {len(files)} images to process.")

    for filename in files:
        full_path = os.path.join(IMAGES_DIR, filename)
        
        # Read Image
        original = cv2.imread(full_path)
        if original is None:
            print(f"⚠️ Failed to load: {filename}")
            continue

        print(f">> Processing: {filename}...")

        # Extract Exercises
        if model:
            crops = extract_crops_yolo(model, original)
        else:
            crops = extract_crops_heuristic(original)
        
        # Segment Digits & Show
        process_and_display(filename, crops)