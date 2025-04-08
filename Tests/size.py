import os
import json
import cv2
import math
import numpy as np

particle_id_counter = 0

def load_pixels_per_mm(config_path="../config.json"):
    """
    Load the pixels_per_mm value from the config.json file.
    Example structure:
    {
      "scaling_factor": {
          "pixels_per_mm": 123.4
      }
    }
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        scaling_factor = float(config["scaling_factor"]["pixels_per_mm"])  # px/mm
        return scaling_factor
    except (FileNotFoundError, KeyError, json.JSONDecodeError, TypeError) as e:
        return 1.0

def load_grayscale(image_path):
    """
    Loads an image from disk and converts it to grayscale.
    """
    img_bgr = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise IOError(f"Could not read image: {image_path}")
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), img_bgr

def measure_particles_from_contours(contours, microns_per_pixel=1.0,
                                    min_area=5, max_area=1e6):
    """
    Given a list of contours, compute size (diameter) assuming each is circular.
    Returns a list of (cx, cy, diameter_um, contour).
    """
    measurements = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area or area > max_area:
            continue

        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # (1) Area-based diameter, assuming circle
        area_diameter_pixels = math.sqrt(4.0 * area / math.pi)
        area_diameter_um = area_diameter_pixels * microns_per_pixel

        is_elliptical = False
        ellipse_info = None
        ellipse_diameter_um = None
        major_axis_um = None
        minor_axis_um = None
        aspect_ratio = None

        if len(cnt) >= 5:
            # Fit ellipse
            ellipse = cv2.fitEllipse(cnt)
            (center_x, center_y), (MA, ma), angle = ellipse
            # MA and ma are in pixels (major axis, minor axis)
            major_axis_um = MA * microns_per_pixel
            minor_axis_um = ma * microns_per_pixel

            # Aspect ratio
            if MA > 0:
                aspect_ratio = ma / MA
            else:
                aspect_ratio = 1.0  # fallback

            # Consider it elliptical if aspect ratio is sufficiently far from 1
            # (adjust threshold as needed, e.g., < 0.95 or < 0.90)
            if aspect_ratio < 0.9:
                is_elliptical = True

            # Compute "average diameter" from major/minor axis
            avg_diam_pixels = 0.5 * (MA + ma)
            ellipse_diameter_um = avg_diam_pixels * microns_per_pixel

            # Store the ellipse parameters
            ellipse_info = ellipse

        # Collect all into a dictionary
        measurements.append({
            "centroid": (cx, cy),
            "area_diameter_um": area_diameter_um,
            "is_elliptical": is_elliptical,
            "ellipse_diameter_um": ellipse_diameter_um,
            "major_axis_um": major_axis_um,
            "minor_axis_um": minor_axis_um,
            "aspect_ratio": aspect_ratio,
            "contour": cnt,
            "ellipse_info": ellipse_info
        })

    return measurements


def draw_results_on_image(image_bgr, measurements, contour_color=(255,0,0), ellipse_color=(255, 0, 0), thickness=1):
    """
    Draw the contour and annotate diameter in microns on a copy of the original BGR image.
    """
    result_img = image_bgr.copy()
    for meas in measurements:
        cnt = meas["contour"]
        cx, cy = meas["centroid"]
        area_diam = meas["area_diameter_um"]
        ellipse_diam = meas["ellipse_diameter_um"]
        ellipse_info = meas["ellipse_info"]
        is_elliptical = meas["is_elliptical"]

        # 1) Draw the contour in red
        cv2.drawContours(result_img, [cnt], -1, contour_color, thickness)

        # 2) If ellipse was successfully fit, optionally draw it in green
        # if ellipse_info is not None:
        #     cv2.ellipse(result_img, ellipse_info, ellipse_color, thickness)
        #
        # # 3) Choose label text
        # if is_elliptical and ellipse_diam is not None:
        #     text_label = f"{ellipse_diam:.1f} um"
        # else:
        text_label = f"{area_diam:.1f} um"

        # 4) Put text near the centroid
        cv2.putText(
            result_img,
            text_label,
            (cx + 5, cy + 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    return result_img

def method_1_otsu_threshold(image_path, microns_per_pixel=1.0):
    gray, img_bgr = load_grayscale(image_path)

    # 1) Slight blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 2) Otsu’s threshold
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # 3) Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 4) Measure the particles from contours
    measurements = measure_particles_from_contours(
        contours,
        microns_per_pixel=microns_per_pixel,
        min_area=4,
        max_area=1e6
    )

    # 5) Draw results
    result_img = draw_results_on_image(img_bgr, measurements, contour_color=(255, 0, 0), ellipse_color=(255, 0, 0))

    return result_img, measurements


def method_3_watershed(image_path, microns_per_pixel=1.0):
    gray, img_bgr = load_grayscale(image_path)

    kernel_tophat = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel_tophat)

    # (b) Slight blur to reduce noise (tune as needed)
    blurred = cv2.GaussianBlur(tophat, (5, 5), 0)

    # 1) Basic Otsu threshold (or any other threshold) to find "sure foreground"
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # 2) Morphological opening to remove noise
    # 3) (Optional) Morphological closing
    #    If your particles have small holes or are slightly fragmented,
    #    a closing step can help unify them.
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close, iterations=1)

    # 4) Morphological opening to remove small noise
    #    Use fewer iterations or smaller kernel to avoid losing tiny particles.
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_open, iterations=1)

    # 3) Sure background by dilating the opening result
    sure_bg = cv2.dilate(opened, kernel_open, iterations=2)

    # 4) Distance transform for the "sure foreground"
    dist_transform = cv2.distanceTransform(opened, cv2.DIST_L2, 5)

    # 5) Threshold distance transform to define the sure foreground region
    dist_thresh = 0.5 * dist_transform.max()
    _, sure_fg = cv2.threshold(dist_transform, dist_thresh, 255, 0)
    sure_fg = np.uint8(sure_fg)

    # 6) Unknown region (neither sure fg nor sure bg)
    unknown = cv2.subtract(sure_bg, sure_fg)

    # 7) Connected components -> markers
    num_markers, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    # 8) Watershed
    img_for_watershed = img_bgr.copy()
    cv2.watershed(img_for_watershed, markers)

    # 9) Build contours from each unique marker > 1
    measurements = []
    for label_id in range(2, num_markers + 2):
        label_mask = np.uint8(markers == label_id)
        cnts, _ = cv2.findContours(label_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(cnts) == 0:
            continue

        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if area < 5:
                continue

            # --- Compute Centroid ---
            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # --- Area-based diameter (circular assumption) ---
            area_diameter_pixels = math.sqrt((4.0 * area) / math.pi)
            area_diameter_um = area_diameter_pixels * microns_per_pixel

            # --- Ellipse-based measurements ---
            is_elliptical = False
            ellipse_info = None
            ellipse_diameter_um = None
            major_axis_um = None
            minor_axis_um = None
            aspect_ratio = None

            if len(cnt) >= 5:
                ellipse = cv2.fitEllipse(cnt)
                (ex, ey), (MA, ma), angle = ellipse

                major_axis_um = MA * microns_per_pixel
                minor_axis_um = ma * microns_per_pixel

                if MA > 0:
                    aspect_ratio = ma / MA
                else:
                    aspect_ratio = 1.0

                # Consider elliptical if aspect_ratio < some threshold
                if aspect_ratio < 0.9:
                    is_elliptical = True

                avg_diam_pixels = 0.5 * (MA + ma)
                ellipse_diameter_um = avg_diam_pixels * microns_per_pixel
                ellipse_info = ellipse

            # Store dictionary for this particle
            measurements.append({
                "centroid": (cx, cy),
                "area_diameter_um": area_diameter_um,
                "is_elliptical": is_elliptical,
                "ellipse_diameter_um": ellipse_diameter_um,
                "major_axis_um": major_axis_um,
                "minor_axis_um": minor_axis_um,
                "aspect_ratio": aspect_ratio,
                "contour": cnt,
                "ellipse_info": ellipse_info
            })

    # 10) Draw results
    result_img = img_bgr.copy()
    for meas in measurements:
        cnt = meas["contour"]
        cv2.drawContours(result_img, [cnt], -1, (0, 255, 0), 1)

        ellipse_info = meas["ellipse_info"]
        if ellipse_info is not None:
            cv2.ellipse(result_img, ellipse_info, (255, 0, 0), 1)  # e.g. draw ellipse in blue

        (cx, cy) = meas["centroid"]
        if meas["is_elliptical"] and meas["ellipse_diameter_um"] is not None:
            text = f"{meas['ellipse_diameter_um']:.1f} um"
        else:
            text = f"{meas['area_diameter_um']:.1f} um"

        cv2.putText(
            result_img,
            text,
            (cx + 5, cy + 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )

    return result_img, measurements


def test_all_methods(image_path, microns_per_pixel=1.0):
    print(f"Testing different segmentation methods on {image_path}...")

    # Method 1
    res1, meas1 = method_1_otsu_threshold(image_path, microns_per_pixel)
    cv2.imwrite("method1_otsu.jpg", res1)
    print(f"Method1: Found {len(meas1)} objects. Result saved to method1_otsu.jpg")

    # # Method 2
    # res2, meas2 = method_2_adaptive_threshold(image_path, microns_per_pixel)
    # cv2.imwrite("method2_adaptive.jpg", res2)
    # print(f"Method2: Found {len(meas2)} objects. Result saved to method2_adaptive.jpg")

    # Method 3 (Distance Transform + Watershed)
    res3, meas3 = method_3_watershed(image_path, microns_per_pixel)
    cv2.imwrite("method3_watershed.jpg", res3)
    print(f"Method3: Found {len(meas3)} objects. Result saved to method3_watershed.jpg")


def main():

    # Load pixel-to-mm ratio from config
    pixel_mm_ratio = load_pixels_per_mm()  # px/mm

    # Convert to microns-per-pixel:
    # 1 mm = 1000 microns
    # If we have `pixel_mm_ratio` pixels per mm, then each pixel is (1 / pixel_mm_ratio) mm
    # => (1 / pixel_mm_ratio) * 1000 microns = 1000 / pixel_mm_ratio
    microns_per_pixel = 1000.0 / pixel_mm_ratio

    # Specify the directory containing the test images
    image_directory = "../Test Data/Images/"

    # Get a list of image files in the directory
    image_files = [f for f in os.listdir(image_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]

    for image_file in image_files:
        # Load the image
        image_path = os.path.join(image_directory, image_file)
        frame = cv2.imread(image_path)

        if frame is None:
            continue

        # Optionally resize the frame if desired
        frame_resized = resize_frame(frame)

        # Step 1: Detect microspheres and store relevant information
        microsphere_data = calculate_and_store_microsphere_data(
            frame_resized,
            microns_per_pixel=microns_per_pixel
        )

        # Print and log each detected particle's size in µm
        for microsphere_id, data in microsphere_data.items():
            size_um = data["size_um"]
            # You can log additional info, e.g. elliptical flags, centroid, etc.
            is_elliptical = data.get("is_elliptical", False)
            cx, cy = data.get("centroid", (0, 0))

            log_str = (
                f"Image: {image_file}, Microsphere ID: {microsphere_id}, "
                f"Size: {size_um:.2f} µm, Elliptical: {is_elliptical}, "
                f"Centroid: ({cx}, {cy})"
            )

            # Print to console
            print(log_str)

        # Optionally annotate the frame with bounding ellipses or ID/size
        # and show it
        frame_with_annotations = annotate_frame_with_microsphere_data(
            frame_resized,
            microsphere_data
        )
        cv2.imshow("Annotated Frame", frame_with_annotations)

        # Exit loop if 'q' key is pressed
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break

    # Close all OpenCV windows
    cv2.destroyAllWindows()

def resize_frame(frame, scale=0.5):
    """Example resizing method. Adapt as needed."""
    h, w = frame.shape[:2]
    new_size = (int(w * scale), int(h * scale))
    return cv2.resize(frame, new_size, interpolation=cv2.INTER_AREA)

def calculate_and_store_microsphere_data(frame, microns_per_pixel=1.0):
    """
    1. Convert to grayscale
    2. Apply morphological top-hat
    3. Threshold and find contours
    4. For each contour, measure size in µm
    5. Return a dictionary of the form:
       { microsphere_id: { "size_um": <float>, "is_elliptical": <bool>, "centroid": (cx, cy) }, ... }
    """
    global particle_id_counter

    result_img = frame.copy()
    # Parameters
    kernel = np.ones((5, 5), np.uint8)
    min_area = 4
    elliptical_thresh = 0.8  # aspect ratio threshold to flag elliptical
    max_area = 1e6  # Optional upper bound for extremely large blobs
    min_size_for_blob = 80  # connected component

    # 1) Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2) Blur to reduce salt-and-pepper noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3) Top-hat to highlight bright regions on uneven background
    tophat = cv2.morphologyEx(blurred, cv2.MORPH_TOPHAT, kernel)

    # 4) Morphological closing to merge bright spots from same particle
    #    Increase kernel size if your particles are large or have bigger gaps
    closed = cv2.morphologyEx(tophat, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 5) Otsu's Threshold
    #    This chooses threshold automatically based on image histogram
    _, binary = cv2.threshold(closed, 50, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    cv2.imshow("Binary", binary)
    adaptive_thresh = cv2.adaptiveThreshold(
        tophat,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # or cv2.ADAPTIVE_THRESH_MEAN_C
        cv2.THRESH_BINARY,
        3,  # blockSize for local region
        2  # constant subtracted from the mean
    )

    # # 6) Remove small connected components
    # nb_components, labels, stats, centroids = cv2.connectedComponentsWithStats(adaptive_thresh, connectivity=8)
    # sizes = stats[1:, cv2.CC_STAT_AREA]
    # nb_components = nb_components - 1
    #
    # binary_filtered = np.zeros(labels.shape, dtype=np.uint8)
    # for i in range(nb_components):
    #     if sizes[i] >= min_size_for_blob:
    #         binary_filtered[labels == i + 1] = 255

    # 7) Find contours in the cleaned binary mask
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #
    # 6) (Optional) Canny edge detection to refine boundaries further
    #    Combine edge mask with the threshold mask if needed
    #    This can reduce false merges but requires tuning thresholds
    # canny_edges = cv2.Canny(closed, 50, 150)
    # combined_mask = cv2.bitwise_and(adaptive_thresh, canny_edges)
    # binary = combined_mask
    #
    # inverted_binary = cv2.bitwise_not(binary)
    #
    # cv2.imshow("Inverted Binary", inverted_binary)

    # Find contours in the binary mask
    # contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    microsphere_data = {}
    for cnt in contours:
        # Optionally approximate contour to remove jagged edges
        epsilon = 0.01 * cv2.arcLength(cnt, True)
        cnt_approx = cv2.approxPolyDP(cnt, epsilon, True)
        area = cv2.contourArea(cnt_approx)
        if area < min_area or area > max_area:
            continue
        perimeter = cv2.arcLength(cnt_approx, True)
        if perimeter == 0:
            continue

        M = cv2.moments(cnt_approx)
        if M["m00"] == 0:
            continue

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # Check circularity
        circularity = (4.0 * math.pi * area) / (perimeter * perimeter)

        # Assume circular shape by default
        diameter_pixels = math.sqrt(4 * area / math.pi)
        diameter_um = diameter_pixels * microns_per_pixel

        is_elliptical = False
        ellipse_params = None

        # If the contour has enough points, try fitting an ellipse
        if len(cnt_approx) >= 5:
            ellipse = cv2.fitEllipse(cnt_approx)
            (ex, ey), (MA, ma), angle = ellipse  # major/minor axes in pixels

            # Check aspect ratio
            aspect_ratio = min(MA, ma) / max(MA, ma)
            if aspect_ratio < elliptical_thresh:
                is_elliptical = True

            # Compute size using average of major/minor axes
            diameter_pixels = (MA + ma) / 2.0
            diameter_um = diameter_pixels * microns_per_pixel
            ellipse_params = ellipse

        # Create a new ID for each contour (or track them if needed)
        particle_id_counter += 1
        sphere_id = particle_id_counter

        # Store results
        microsphere_data[sphere_id] = {
            "size_um": diameter_um,
            "is_elliptical": is_elliptical,
            "centroid": (cx, cy),
            "contour": cnt,  # <--- store actual contour
            "ellipse": ellipse_params,  # <--- store fitted ellipse if any
            "circularity": circularity
        }

    return microsphere_data

def annotate_frame_with_microsphere_data(frame, microsphere_data):
    """
    Annotate the frame by:
      - Drawing the actual contour in green.
      - If the particle is elliptical, drawing a fitted ellipse in red.
      - Drawing text for ID and size near the centroid.
    """
    for pid, data in microsphere_data.items():
        cx, cy = data["centroid"]
        size_um = data["size_um"]
        contour = data["contour"]             # The stored contour
        ellipse = data.get("ellipse", None)   # The stored ellipse (if any)
        # is_elliptical = data["is_elliptical"]

        # 1. Draw the actual contour in green to show the real shape
        cv2.drawContours(frame, [contour], -1, (0, 255, 0), 1)

        # # 2. If flagged as elliptical, draw the fitted ellipse in red
        # if is_elliptical and ellipse is not None:
        #     cv2.ellipse(frame, ellipse, (0, 0, 255), 1)

        # 3. Annotate the ID and size in microns near the centroid
        text = f"ID:{pid}, {size_um:.1f}um"
        cv2.putText(frame, text, (cx + 10, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    return frame

if __name__ == "__main__":
    # main()
    test_all_methods("../Test Data/Images/4825microspheres.jpg", microns_per_pixel=42.68)





def method_2_adaptive_threshold(image_path, microns_per_pixel=1.0):
    # 1) LOAD IMAGE
    gray, img_bgr = load_grayscale(image_path)

    # 2) TOP-HAT (Optional, to remove uneven background if particles are bright)
    #    Increase kernel size if background variation is large
    # kernel_tophat = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    # tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel_tophat)

    # 3) GAUSSIAN BLUR (Helps reduce local noise before adaptive threshold)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 4) ADAPTIVE THRESHOLD
    #    - Use a smaller blockSize if your particles are small or finely spaced
    #    - For heavily uneven backgrounds, experiment with bigger blockSize
    #    - 'C' adjusts bias; if you see too many or too few detections, tweak it
    block_size = 11  # or 31; must be odd
    C = 7            # tune (+/-) based on brightness

    adaptive = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,  # or cv2.THRESH_BINARY_INV if needed
        block_size,
        C
    )

    # 5) MORPHOLOGICAL REFINEMENT
    #    a) CLOSE small gaps/holes if your particles are broken
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    closed = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel_close, iterations=1)

    #    b) OPEN to remove small noise ("salt" noise)
    # kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    # cleaned = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_open, iterations=1)

    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dilated = cv2.dilate(closed, kernel_dilate, iterations=1)
    cleaned = dilated

    # 6) FIND CONTOURS
    contours, _ = cv2.findContours(
        cleaned,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # 7) MEASURE PARTICLES
    measurements = measure_particles_from_contours(
        contours,
        microns_per_pixel=microns_per_pixel,
        min_area=4,
        max_area=1e6
    )

    # 8) DRAW RESULTS
    result_img = draw_results_on_image(
        img_bgr,
        measurements,
        contour_color=(255, 0, 0),  # blue
        ellipse_color=(0, 255, 0),  # green
        thickness=1
    )

    return result_img, measurements
























# import os
# import json
# import cv2
# import logging
# from OpticalMetrologyModule import OpticalMetrologyModule
#
# def load_pixels_per_mm(config_path="../config.json"):
#     """
#     Load the pixels_per_mm value from the config.json file.
#
#     :param config_path: Path to the configuration file.
#     :return: pixels_per_mm value (float) or None if not found.
#     """
#     try:
#         with open(config_path, 'r') as f:
#             config = json.load(f)
#         scaling_factor = float(config["scaling_factor"]["pixels_per_mm"])  # Access nested value
#         return scaling_factor
#     except (FileNotFoundError, KeyError, json.JSONDecodeError, TypeError) as e:
#         logging.error(f"Error loading pixels_per_mm: {e}. Using default 1.0")
#         return 1.0
#
# def setup_logging():
#     """Setup logging with file clearing."""
#     log_file = 'microsphere_size_test_log.txt'
#     # Clear the log file
#     with open(log_file, 'w') as f:
#         f.write('')
#     # Setup logging configuration
#     logging.basicConfig(
#         filename=log_file,
#         level=logging.INFO,
#         format="%(asctime)s - %(levelname)s - %(message)s"
#     )
#
# def main():
#     # Clear and setup logging first
#     setup_logging()
#
#     # Create an instance of OpticalMetrologyModule
#     optical_metrology_module = OpticalMetrologyModule(debug=False)
#
#     # Specify the directory containing the test images
#     image_directory = "../Test Data/Images/"
#
#     # Define pixel-to-mm ratio for size conversion (use calibrated value)
#     pixel_mm_ratio = load_pixels_per_mm()
#
#     # Get a list of image files in the directory
#     image_files = [f for f in os.listdir(image_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
#
#     for image_file in image_files:
#         # Load the image
#         image_path = os.path.join(image_directory, image_file)
#         frame = cv2.imread(image_path)
#
#         if frame is None:
#             logging.error(f"Failed to load image: {image_file}")
#             continue
#
#         frame_resized = optical_metrology_module.resize_frame(frame)
#
#         # Process the image to get microsphere information
#         # optical_metrology_module.initialize_features(frame_resized, False)
#
#         # Step 1: Detect microspheres and store relevant information
#         microsphere_data = optical_metrology_module.calculate_and_store_microsphere_data(frame_resized)
#
#         # Log the size information for each microsphere detected in the image
#         # for microsphere_id, size_in_pixels in optical_metrology_module.microsphere_sizes.items():
#         #     # Convert size from pixels to millimeters
#         #     print(f"Size in pixels: {size_in_pixels}")
#         #     size_in_um = (size_in_pixels / 41.1)*1000
#         #     logging.info(f"Image: {image_file}, Microsphere ID: {microsphere_id}, Size: {size_in_um:.3f} um")
#         #     print(f"Image: {image_file}, Microsphere ID: {microsphere_id}, Size: {size_in_um:.2f} um")
#
#         # Log the size information for each microsphere detected
#         for microsphere_id, data in microsphere_data.items():
#             size_in_pixels = data["size"]  # Extract size from the stored data
#             size_in_um = (size_in_pixels / 41.1) * 1000  # Convert to micrometers
#             logging.info(f"Image: {image_file}, Microsphere ID: {microsphere_id}, Size: {size_in_um:.3f} um")
#             print(f"Image: {image_file}, Microsphere ID: {microsphere_id}, Size: {size_in_um:.2f} um")
#
#         frame_with_annotations = optical_metrology_module.annotate_frame_with_microsphere_data(frame_resized,
#                                                                                                microsphere_data)
#
#         # Optionally, display the annotated frame
#         cv2.imshow("Annotated Frame", frame_with_annotations)
#
#         # Optionally, display the image with detected features
#         # frame_with_ids = optical_metrology_module.annotate_frame_with_ids(frame_resized, optical_metrology_module.microsphere_sizes)
#         # cv2.imshow("Detected Particles", frame_with_ids)
#
#         # Exit loop if 'q' key is pressed
#         if cv2.waitKey(0) & 0xFF == ord('q'):
#             break
#
#     # Close all OpenCV windows
#     cv2.destroyAllWindows()
#
# if __name__ == "__main__":
#     main()