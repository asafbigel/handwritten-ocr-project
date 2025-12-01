import cv2 as cv
import matplotlib.pyplot as plt
import sys

def load_and_inspect_image(img_path):
    """
    Loads an image from the given path, prints its properties, and returns it.
    Exits if the image cannot be loaded.
    """
    image = cv.imread(img_path)

    if image is None:
        print(f"Error: Could not load image from path: {img_path}")
        sys.exit()

    print("--- Image Properties ---")
    print(f"Type: {type(image)}")
    print(f"Shape: {image.shape}")
    print(f"Data Type: {image.dtype}")
    # Let's look at a single pixel value at [100, 100]
    px = image[100, 100]
    print(f"Pixel at [100,100] (BGR): {px}")
    print("------------------------")
    return image

def preprocess_image(image):
    """
    Applies preprocessing steps to the image:
    1. Grayscale conversion
    2. Gaussian blur
    3. Adaptive thresholding
    Returns the processed images.
    """
    # We don't need color for digit recognition. It's noise.
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    print(f"Gray Shape: {gray.shape}")  # Notice channels are gone. It's 2D now.

    # Further processing
    gaussian_blurred = cv.GaussianBlur(gray, (5, 5), -5)
    thresholded = cv.adaptiveThreshold(gaussian_blurred, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv.THRESH_BINARY_INV, 11, 10)
    
    return gray, gaussian_blurred, thresholded

def visualize_steps(original, gray, gaussian_blurred, thresholded_image):
    """
    Visualizes the original image and the preprocessing steps.
    """
    plt.figure(figsize=(10, 10))
    
    plt.subplot(2, 2, 1)
    plt.title("Original (BGR converted to RGB for plot)")
    plt.imshow(cv.cvtColor(original, cv.COLOR_BGR2RGB))
    
    plt.subplot(2, 2, 2)
    plt.title("Grayscale")
    plt.imshow(gray, cmap='gray')

    plt.subplot(2, 2, 3)
    plt.title("Gaussian Blurred")
    plt.imshow(gaussian_blurred, cmap='gray')

    plt.subplot(2, 2, 4)
    plt.title("Adaptive Threshold")
    plt.imshow(thresholded_image, cmap='gray')
    
    plt.tight_layout()
    plt.show()

def main(img_path):
    """
    Main function to run the image loading, preprocessing, and visualization pipeline.
    """
    image = load_and_inspect_image(img_path)
    gray, gaussian_blurred, thresholded_image = preprocess_image(image)
    visualize_steps(image, gray, gaussian_blurred, thresholded_image)

if __name__ == '__main__':
    # Make sure path is correct
    img_path = r'C:\Users\asafb\Desktop\Projects\handwritten-ocr-project\data\raw\sample_1.jpg'
    main(img_path)