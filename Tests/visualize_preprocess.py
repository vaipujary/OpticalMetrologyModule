import cv2
import numpy as np


def visualize_preprocessing(image_path):
    """Visualizes the preprocessing steps of the Optical Metrology Module."""
    # Load the input image
    frame = cv2.imread(image_path)
    if frame is None:
        print("Error: Unable to load the image.")
        return

    # Step 1: Display Original Image
    cv2.imshow("Step 1: Original Image", frame)
    cv2.waitKey(0)

    # Step 2: Convert to Grayscale
    if len(frame.shape) == 2:  # Grayscale image
        gray = frame
    elif frame.shape[2] == 1:
        gray = frame
    else:  # Convert to grayscale if it's not already.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Step 2: Grayscale Image", gray)
    cv2.waitKey(0)

    # Step 3: CLAHE for Contrast Enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    cv2.imshow("Step 3: CLAHE Enhanced Image", enhanced)
    cv2.waitKey(0)

    # Step 4: Gaussian Blur
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    cv2.imshow("Step 4: Gaussian Blurred Image", blurred)
    cv2.waitKey(0)

    # Step 5: Otsu's Thresholding
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cv2.imshow("Step 5: Binary Image (Thresholded)", binary)
    cv2.waitKey(0)

    # Step 6: Invert Binary Image
    inverted_binary = cv2.bitwise_not(binary)
    cv2.imshow("Step 6: Inverted Binary Image", inverted_binary)
    cv2.waitKey(0)

    # Step 7: Find Contours
    contours, _ = cv2.findContours(inverted_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    debug_contours_frame = frame.copy()
    cv2.drawContours(debug_contours_frame, contours, -1, (0, 0, 255), 1)
    cv2.imshow("Step 7: Contours Overlaid on Original Image", debug_contours_frame)
    cv2.waitKey(0)

    # Clean up OpenCV windows
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Path to the input image
    image_path = "../Test Data/Images/Microspheres8.png"  # Replace this with the path to your input image
    visualize_preprocessing(image_path)
