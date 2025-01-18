import os
import cv2
import logging
from OpticalMetrologyModule import OpticalMetrologyModule

def main():
    # Set up logging configuration.
    logging.basicConfig(filename='microsphere_size_test_log.txt', level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Create an instance of OpticalMetrologyModule
    optical_metrology_module = OpticalMetrologyModule()

    # Specify the directory containing the test images
    image_directory = "../Test Data/Images"  # Replace with the path to your dust particle images

    # Get a list of image files in the directory
    image_files = [f for f in os.listdir(image_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]

    for image_file in image_files:
        # Load the image
        image_path = os.path.join(image_directory, image_file)
        frame = cv2.imread(image_path)

        if frame is None:
            logging.error(f"Failed to load image: {image_file}")
            continue

        # Process the image to get microsphere information
        optical_metrology_module.initialize_features(frame, False)

        # Log the size information for each microsphere detected in the image
        for microsphere_id, size in optical_metrology_module.microsphere_sizes.items():
            logging.info(f"Image: {image_file}, Microsphere ID: {microsphere_id}, Size: {size:.2f} pixels")

        # Optionally, display the image with detected features
        for feature in optical_metrology_module.prev_features:
            x, y = feature.ravel()
            cv2.circle(frame, (int(x), int(y)), 3, (0, 0, 255), -1)

        cv2.imshow("Dust Particles", frame)
        # Exit loop if 'q' key is pressed
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break

    # Close all OpenCV windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
