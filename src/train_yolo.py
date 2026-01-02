import os
import random
import json
from ultralytics import YOLO

# 1. הגדרת נתיבים וקבצים
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
image_dir = os.path.join(root_dir, 'data', 'dataset', 'images')
train_txt = os.path.join(root_dir, 'data', 'dataset', 'train.txt')
val_txt = os.path.join(root_dir, 'data', 'dataset', 'val.txt')
meta_file = os.path.join(root_dir, 'training_metadata.json')
model_path = os.path.join(root_dir, 'runs', 'detect', 'handwritten_random_split3', 'weights', 'best.pt')

# 2. חלוקה מחדש אקראית (Cross-Validation effect)
print("Re-shuffling dataset for dynamic split...")
images = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
random.shuffle(images)
split_idx = int(len(images) * 0.8)

with open(train_txt, 'w') as f:
    for img in images[:split_idx]: f.write(img + '\n')
with open(val_txt, 'w') as f:
    for img in images[split_idx:]: f.write(img + '\n')

# 3. ניהול מונה Epochs
if os.path.exists(meta_file):
    with open(meta_file, 'r') as f: metadata = json.load(f)
else:
    metadata = {"total_epochs": 0, "runs_count": 0}

epochs_to_run = 50 # כמה לאמן בסיבוב הזה
metadata["total_epochs"] += epochs_to_run
metadata["runs_count"] += 1

# 4. בחירת מודל: המשך מ-best.pt או התחלה מ-yolov8n.pt
if os.path.exists(model_path):
    print(f"Loading existing best model from {model_path}...")
    model = YOLO(model_path)
else:
    print("No existing model found. Starting from scratch with yolov8n.pt...")
    model = YOLO('yolov8n.pt')

# 5. אימון
results = model.train(
    data='dataset_config.yaml',
    epochs=epochs_to_run,
    imgsz=640,
    # --- Disabling Mosaic and mixing ---
    mosaic=0.0,      # Set to 0.0 to disable 4-image stitching 
    mixup=0.0,       # Ensure mixup is also disabled 
    patience=0,
    # -----------------------------------
    # --- Data Augmentation Parameters ---
    degrees=15.0,               # Rotation range (±15 degrees)
    shear=10.0,                 # Shear range (±10 degrees)
    perspective=0.000,          # Perspective transform (0.0 to 0.001)
    # ------------------------------------
    batch=16,
    name='handwritten_no_mosaic',
    exist_ok=True # דורס את התיקייה הקיימת כדי לשמור על סדר
)

# שמירת Metadata מעודכן
with open(meta_file, 'w') as f:
    json.dump(metadata, f, indent=4)

print(f"Training session complete. Total cumulative epochs: {metadata['total_epochs']}")