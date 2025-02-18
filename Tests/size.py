import os
import json
import cv2
import logging
from OpticalMetrologyModule import OpticalMetrologyModule

def load_pixels_per_mm(config_path="../config.json"):
    """
    Load the pixels_per_mm value from the config.json file.

    :param config_path: Path to the configuration file.
    :return: pixels_per_mm value (float) or None if not found.
    """
    if not os.path.exists(config_path):
        logging.error(f"Configuration file not found: {config_path}")
        return None

    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
            return config.get("scaling_factor", {}).get("pixels_per_mm")
    except Exception as e:
        logging.error(f"Failed to read configuration file: {e}")
        return None

def setup_logging():
    """Setup logging with file clearing."""
    log_file = 'microsphere_size_test_log.txt'
    # Clear the log file
    with open(log_file, 'w') as f:
        f.write('')
    # Setup logging configuration
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def main():
    # Clear and setup logging first
    setup_logging()

    # Create an instance of OpticalMetrologyModule
    optical_metrology_module = OpticalMetrologyModule(debug=False)

    # Specify the directory containing the test images
    image_directory = "../Test Data/Images/"

    # Define pixel-to-mm ratio for size conversion (use calibrated value)
    pixel_mm_ratio = load_pixels_per_mm()

    # Get a list of image files in the directory
    image_files = [f for f in os.listdir(image_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]

    for image_file in image_files:
        # Load the image
        image_path = os.path.join(image_directory, image_file)
        frame = cv2.imread(image_path)

        if frame is None:
            logging.error(f"Failed to load image: {image_file}")
            continue

        frame_resized = optical_metrology_module.resize_frame(frame)

        # Process the image to get microsphere information
        optical_metrology_module.initialize_features(frame_resized, False)

        # Log the size information for each microsphere detected in the image
        for microsphere_id, size_in_pixels in optical_metrology_module.microsphere_sizes.items():
            # Convert size from pixels to millimeters
            size_in_um = (size_in_pixels / pixel_mm_ratio)*1000
            logging.info(f"Image: {image_file}, Microsphere ID: {microsphere_id}, Size: {size_in_um:.2f} um")
            print(f"Image: {image_file}, Microsphere ID: {microsphere_id}, Size: {size_in_um:.2f} um")

        # Optionally, display the image with detected features
        frame_with_ids = optical_metrology_module.annotate_frame_with_ids(frame_resized)
        cv2.imshow("Detected Particles", frame_with_ids)

        # Exit loop if 'q' key is pressed
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break

    # Close all OpenCV windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
