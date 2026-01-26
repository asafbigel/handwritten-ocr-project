import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import os

# Configuration
OUTPUT_DIR = "data/synthetic_raw"
NUM_IMAGES = 10
FONT_PATH = "Patrick Hand"  # Ensure this file exists, or change to a system font
IMAGE_SIZE = (640, 640) # YOLOv8 friendly size

def create_noisy_paper(size):
    # Create white background
    img = np.ones((size[1], size[0], 3), dtype=np.uint8) * 255
    
    # Add some gaussian noise to simulate paper texture
    noise = np.random.normal(0, 5, img.shape).astype(np.uint8)
    img = cv2.add(img, noise) # Add noise but keep it white-ish
    return img

def draw_text_pill(cv_img, text, pos, font_path, font_size=30, color=(0, 0, 0)):
    # Convert to PIL Image to use TrueType fonts
    pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Warning: Font '{font_path}' not found. Using default.")
        font = ImageFont.load_default()

    draw.text(pos, text, font=font, fill=color)
    
    # Convert back to OpenCV
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def generate_equation():
    # Generate simple math: A + B = 
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    op = random.choice(['+', '-'])
    
    # Ensure positive results for subtraction
    if op == '-' and a < b:
        a, b = b, a
        
    return f"{a} {op} {b} ="

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"Generating {NUM_IMAGES} synthetic images in '{OUTPUT_DIR}'...")

    for i in range(NUM_IMAGES):
        # 1. Create Base Paper
        img = create_noisy_paper(IMAGE_SIZE)
        
        # 2. Add random equations
        num_exercises = random.randint(3, 6)
        start_y = 50
        
        for j in range(num_exercises):
            eq = generate_equation()
            # Add some jitter to position (simulate human imperfection)
            x_pos = 50 + random.randint(-5, 5)
            y_pos = start_y + (j * 80) + random.randint(-5, 5)
            
            img = draw_text_pill(img, eq, (x_pos, y_pos), FONT_PATH, font_size=40)

        # 3. Save
        filename = os.path.join(OUTPUT_DIR, f"syn_{i:03d}.jpg")
        cv2.imwrite(filename, img)
    
    print("Done. Now go to Roboflow and upload them.")

if __name__ == "__main__":
    main()