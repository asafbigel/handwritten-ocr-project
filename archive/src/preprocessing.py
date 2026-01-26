import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# ==========================================
# SECTION 1: PRODUCTION LOGIC (The "Engine")
# These functions are used by the main system/API.
# ==========================================

def load_and_prep_image(image_path: str) -> np.ndarray:
    """
    Loads an image and prepares it for the model pipeline.
    
    Current Assumption: Input is a scanned, flat document.
    Output: Binary image (White text on Black background).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at: {image_path}")

    img = cv.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to decode image from {image_path}")
    
    # 1. Convert to Grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # 2. Binarization (Thresholding)
    # TODO: In the future, replace fixed threshold (200) with adaptive method (Otsu)
    # CRITICAL: We use THRESH_BINARY_INV so text is White (1) and background is Black (0)
    _, binary = cv.threshold(gray, 200, 255, cv.THRESH_BINARY_INV)
    
    # TODO: Add 'find_document_contours' here for raw camera images (Week 4 logic)
    # TODO: Add 'perspective_transform' here to align the document

    return binary

# ==========================================
# SECTION 2: RESEARCH & DEBUGGING TOOLS
# These functions are for YOU, not the server.
# ==========================================

def load_and_inspect_image(img_path: str) -> np.ndarray:
    """
    Debug function: Loads image and prints verbose properties.
    Useful for understanding input data format.
    """
    image = cv.imread(img_path)

    if image is None:
        print(f"Error: Could not load image from path: {img_path}")
        sys.exit(1) # Exit with error code

    print("--- Image Inspection ---")
    print(f"Type: {type(image)}")
    print(f"Shape: {image.shape}") # (Height, Width, Channels)
    print(f"Data Type: {image.dtype}")
    
    # Check a sample pixel
    if image.shape[0] > 100 and image.shape[1] > 100:
        px = image[100, 100]
        print(f"Pixel at [100,100] (BGR): {px}")
    
    print("------------------------")
    return image

# def run_experimental_pipeline(image: np.ndarray):
#     """
#     Applies a more complex (experimental) preprocessing chain.
#     Used to test new methods before moving them to Production.
#     """
#     # 1. Grayscale
#     gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
#     # 2. Gaussian Blur (Reduce noise)
#     gaussian_blurred = cv.GaussianBlur(gray, (5, 5), 0)
    
#     # 3. Adaptive Thresholding (Better for varying lighting conditions)
#     thresholded = cv.adaptiveThreshold(
#         gaussian_blurred, 
#         255, 
#         cv.ADAPTIVE_THRESH_GAUSSIAN_C,
#         cv.THRESH_BINARY_INV, 
#         11, 
#         10
#     )
    
#     return gray, gaussian_blurred, thresholded

def run_experimental_pipeline(image: np.ndarray):
    # 1. Grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # 2. Gaussian Blur (עדין יותר)
    gaussian_blurred = cv.GaussianBlur(gray, (5, 5), 0)
    
    # 3. Adaptive Thresholding (C=4: פשרה בין רעש לבין שלמות הטקסט)
    thresholded = cv.adaptiveThreshold(
        gaussian_blurred, 
        255, 
        cv.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv.THRESH_BINARY_INV, 
        11,  # Block Size
        8    # C parameter: הורדנו מ-10 ל-4 כדי להחזיר את האותיות שנעלמו
    )
    
    # 4. Morphological Dilation (הדבק)
    # זה יחבר את האותיות השבורות ויהפוך אותן ל"שמנות" יותר
    kernel = np.ones((2,2), np.uint8) # קרנל קטן ועדין
    dilated = cv.dilate(thresholded, kernel, iterations=1)
    
    return gray, gaussian_blurred, dilated

def segment_digits(binary_image: np.ndarray, min_area: int = 100):
    """
    Week 8 Core Logic:
    Takes a BINARY image, finds individual digits, and sorts them Left-to-Right.
    """
    # 1. Find Contours (Only outer shapes, imply no holes inside 8 or 0)
    contours, _ = cv.findContours(binary_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    valid_items = []
    
    # 2. Filter Noise & Collect
    for c in contours:
        x, y, w, h = cv.boundingRect(c)
        
        # Filter: Ignore small dots/noise
        if w * h < min_area:
            continue
            
        valid_items.append((x, y, w, h))
        
    # 3. Sort Left-to-Right (CRITICAL for Math Logic!)
    # We sort the list based on the 'x' coordinate
    sorted_items = sorted(valid_items, key=lambda item: item[0])
    
    return sorted_items

def visualize_steps(original, gray, blurred, thresholded):
    """
    Plotting utility to see the stages side-by-side.
    """
    plt.figure(figsize=(12, 8))
    
    titles = ["Original", "Grayscale", "Blurred", "Adaptive Thresh (Binary)"]
    images = [
        cv.cvtColor(original, cv.COLOR_BGR2RGB),
        gray,
        blurred,
        thresholded
    ]
    
    for i in range(4):
        plt.subplot(2, 2, i+1)
        plt.title(titles[i])
        # If the image is grayscale, we need to tell pyplot to use gray colormap
        if len(images[i].shape) == 2:
            plt.imshow(images[i], cmap='gray')
        else:
            plt.imshow(images[i])
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()

# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == '__main__':
    # TODO: Replace hardcoded path with argparse or environment variable
    # Example: img_path = sys.argv[1] if len(sys.argv) > 1 else 'default.jpg'
    
    # Use raw string (r'...') for Windows paths
    # Note: Make sure this file actually exists on your disk!
    img_path = r'C:\Users\asafb\Desktop\Projects\handwritten-ocr-project\data\raw\sample_1.jpg'
    
    if os.path.exists(img_path):
        print(f"Processing: {img_path}")
        
        # 1. Inspect
        original = load_and_inspect_image(img_path)
        
        # 2. Run Preprocessing (Get the binary image)
        # אנחנו משתמשים בפונקציה הקיימת שלך כדי לקבל את התמונה הבינארית (המשתנה השלישי)
        gray, blurred, binary_result = run_experimental_pipeline(original)
        
        # 3. Visualize Preprocessing Steps (Optional - אפשר להשאיר בהערה כדי לא להעמיס)
        # visualize_steps(original, gray, blurred, binary_result)
        
        # 4. Run Segmentation (WEEK 8 LOGIC)
        # זה החלק החדש: לוקחים את התמונה הבינארית ומפרקים אותה לגורמים
        print("\n>> Running Digit Segmentation (Week 8)...")
        try:
            boxes = segment_digits(binary_result)
            print(f"Found {len(boxes)} symbols.")
            
            # 5. Visual Validation (Draw boxes on original)
            debug_img = original.copy()
            for i, (x, y, w, h) in enumerate(boxes):
                # Draw rectangle: Green, Thickness 2
                cv.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # Draw index number (to verify Left-to-Right sorting)
                cv.putText(debug_img, str(i), (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                
            plt.figure(figsize=(10, 6))
            plt.imshow(cv.cvtColor(debug_img, cv.COLOR_BGR2RGB))
            plt.title(f"Segmentation Result: {len(boxes)} Digits Found (Sorted L->R)")
            plt.axis('off')
            plt.show()
            
        except NameError:
            print("CRITICAL ERROR: הפונקציה 'segment_digits' לא נמצאה.")
            print("ודא שהעתקת את SECTION 3 (הפונקציה החדשה) והדבקת אותה לפני ה-main.")

    else:
        print(f"CRITICAL: File not found at {img_path}")
        print("Please update the path in main() or add a sample image.")