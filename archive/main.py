import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from src.segmentation import segment_digits

def load_image(path):
    return cv2.imread(path)

def preprocess_debug_pipeline(image):
    """
    מחזיר את כל שלבי הביניים כדי שנוכל לראות מה קורה בכל שלב
    """
    # שלב 1: אפור
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # שלב 2: טשטוש (להורדת רעש נייר)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # שלב 3: Adaptive Threshold (הכי חשוב!)
    # נסה לשחק עם ה-C (הפרמטר האחרון: 4, 6, 8) אם יש יותר מדי רעש
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 8 
    )
    
    # שלב 4: ניקוי מורפולוגי (אופציונלי - כרגע מכובה)
    # kernel = np.ones((2,2), np.uint8)
    # dilated = cv2.dilate(thresh, kernel, iterations=1)
    
    return gray, blurred, thresh

import math

def visualize_dynamic(steps_list):
    """
    כלי דינמי להצגת תמונות.
    מקבל רשימה של (כותרת, תמונה) ומסדר אותן בגריד אוטומטי.
    Args:
        steps_list: List[Tuple[str, np.ndarray]] -> [("Title 1", img1), ("Title 2", img2)...]
    """
    n = len(steps_list)
    if n == 0: return

    # חישוב גריד אוטומטי (מקסימום 3 בשורה)
    cols = 3 if n >= 3 else n
    rows = math.ceil(n / cols)
    
    # גודל התצוגה תלוי בכמות התמונות
    plt.figure(figsize=(5 * cols, 5 * rows))
    
    for i, (title, img) in enumerate(steps_list):
        plt.subplot(rows, cols, i + 1)
        plt.title(title)
        
        # טיפול בתמונות שחור-לבן מול צבעוניות
        if len(img.shape) == 2: # Grayscale/Binary
            plt.imshow(img, cmap='gray')
        else: # BGR (OpenCV standard)
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            
        plt.axis('off')
        
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # ודא שהנתיב נכון!
    img_path = r'C:\Users\asafb\Desktop\Projects\handwritten-ocr-project\data\raw\sample_1.jpg'
    
    if os.path.exists(img_path):
        print(f">> Processing: {img_path}")
        original = load_image(img_path)
        
        # הרצת ה-Pipeline וקבלת כל שלבי הביניים
        gray, blurred, binary = preprocess_debug_pipeline(original)
        
        # הרצת הסגמנטציה על התוצאה הבינארית
        print(">> Running Segmentation...")
        # min_area=50: מסנן רעשים קטנים מאוד
        boxes = segment_digits(binary, min_area=20) 
        print(f">> Found {len(boxes)} symbols.")
        
        final_result_img = original.copy()
        for i, (x, y, w, h) in enumerate(boxes):
            cv2.rectangle(final_result_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(final_result_img, str(i), (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # הצגת הלוח
        visualize_dynamic([("Original", original), ("Grayscale", gray), ("Blurred", blurred), ("Binary", binary)])
        visualize_dynamic([("Binary", binary), ("final result img", final_result_img)])
        
    else:
        print("Error: Image not found.")