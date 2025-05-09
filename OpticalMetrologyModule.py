import cv2
import numpy as np
import csv
import os
import json
import logging

# 355-425 um


class OpticalMetrologyModule:
    def __init__(self, debug=False, output_csv="particle_data.csv", config_path=os.path.join(os.path.dirname(__file__), 'config.json'), fps=30, parent_ui=None):
        # Initialize previous frame and features to None
        self.prev_gray = None
        self.prev_features = None
        self.next_particle_id = 1  # Start assigning particle IDs from 1
        self.microsphere_ids = [] # Uses sequential numeric IDs for particles
        self.microsphere_sizes = {}  # Dictionary to store the size of each microsphere
        self.trajectories = {}  # Dictionary to store trajectories of each microsphere
        self.microsphere_positions = {}  # Store positions for all particles
        self.microsphere_velocities = {}  # Store velocities for all particles

        self.frame_number = 0  # Keep track of the current frame number
        # Parameters for Lucas-Kanade optical flow
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.csv_file = output_csv  # Path to the output CSV file
        self.fps = fps  # Frame rate of the video
        self.debug = debug
        self.persistent_debug_frame = None
        self.parent_ui = parent_ui
        # Load pixel-to-mm scaling factor from config.json
        self.scaling_factor = self.load_config(config_path)

        # Initialize CSV file and write the header
        self.initialize_csv()

    def load_config(self, config_path):
        """
        Load the pixel-to-mm scaling factor from the JSON configuration file.

        :param config_path: Path to the configuration JSON file.
        :return: Pixels-per-mm scaling factor.
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            scaling_factor = float(config["scaling_factor"]["pixels_per_mm"])  # Access nested value
            return scaling_factor
        except (FileNotFoundError, KeyError, json.JSONDecodeError, TypeError) as e:
            logging.error(f"Error loading pixels_per_mm: {e}. Using default 1.0")
            return 1.0

    def initialize_csv(self):
        """Initialize the CSV file and write the header."""
        with open(self.csv_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["Frame", "Timestamp (s)", "Particle ID", "X (mm)", "Y (mm)", "Size (um)", "Velocity (mm/s)",
                 "Trajectory (mm)"])

    def log_to_csv(self, frame_number, particle_id, x, y, size, velocity, trajectory, save_data_enabled=False):
        """Log particle data into the CSV file."""

        # Only log data if the checkbox is checked
        if not save_data_enabled:
            if self.debug:
                logging.info("Save Data option is disabled. Skipping CSV logging.")
            return  # Do nothing if not checked

        timestamp = frame_number / self.fps  # Calculate timestamp in seconds

        # Validate the data before writing
        if not self.validate_row(frame_number, timestamp, particle_id, x, y, size, velocity, trajectory):
            if self.debug:
                logging.warning(f"Invalid data ignored for Particle ID {particle_id} in Frame {frame_number}")
            return  # Skip invalid data

        with open(self.csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([frame_number, timestamp, particle_id, x, y, size, velocity, trajectory])

    def resize_frame(self, image, max_width=800, max_height=600):
        """
        Resize an image to fit within a specified maximum width and height while maintaining the aspect ratio.

        :param image: The input image.
        :param max_width: Maximum width for resizing.
        :param max_height: Maximum height for resizing.
        :return: Resized image.
        """
        h, w = image.shape[:2]

        # Compute the scaling factor to maintain the aspect ratio
        scale = min(max_width / w, max_height / h)

        # Resize the image using the computed scale
        new_width = int(w * scale)
        new_height = int(h * scale)
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        return resized_image

    def initialize_features(self, current_frame, is_reduce_noise):
        # Ensure current_frame is not single channel before conversion.
        if len(current_frame.shape) == 3 and current_frame.shape[2] > 1:  # Check for multi-channel
            gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        elif len(current_frame.shape) == 2 or (len(current_frame.shape) == 3 and current_frame.shape[2] == 1):
            gray = current_frame  # Don't convert if it's already single-channel/grayscale
            if self.debug:
                print("Warning: initialize_features received a single-channel image.")
        else:
            # Handle unexpected image format - perhaps raise an error and log the issue
            raise ValueError("Unexpected image format in initialize_features. Check the input frame's shape.")

        if is_reduce_noise:
            current_frame = cv2.GaussianBlur(current_frame, (3, 3), 0)

            # Initialize the persistent debug frame as a copy of the current frame
        if self.persistent_debug_frame is None:
            self.persistent_debug_frame = current_frame.copy()

        # Display the original grayscale image for debugging
        if self.debug:
            cv2.imshow("Original Grayscale Image", gray)
            cv2.waitKey(0)

        # Detect good features to track using Shi-Tomasi corner detection
        self.prev_features = cv2.goodFeaturesToTrack(
            gray,
            maxCorners=2000, # Allow more points to be detected
            qualityLevel=0.01, # Lower sensitivity threshold for detecting weaker features
            minDistance=5, # Reduce distance to detect smaller, closely packed particles
            blockSize=5,          # Increased block size for better feature detection
            useHarrisDetector=True,  # Use Harris corner detector
            k=0.04) # Smaller block size to focus on finer details

        # Display detected features for debugging
        if self.debug and self.prev_features is not None:
            debug_features_frame = current_frame.copy()
            for feature in self.prev_features:
                x, y = feature.ravel()
                cv2.circle(debug_features_frame, (int(x), int(y)), 3, (0, 255, 0), -1)
            cv2.imshow("Detected Features", debug_features_frame)
            cv2.waitKey(0)

        # Only proceed if features were detected
        if self.prev_features is None or len(self.prev_features) == 0:
            print("No features detected in frame")
            return

        print(f"Detected {len(self.prev_features)} features")

        # Refine features to subpixel accuracy
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        self.prev_features = cv2.cornerSubPix(
            gray,
            self.prev_features,
            winSize=(5, 5),  # Search window size
            zeroZone=(-1, -1),
            criteria=criteria
        )

        # Try using SIFT
        # Detect features using SIFT
        # try:
        #     sift = cv2.SIFT_create()
        #     print("SIFT is available and working!")
        #     keypoints = sift.detect(gray, None)
        # except AttributeError:
        #     print("SIFT is not available. Make sure OpenCV-Contrib is installed.")
        #
        #
        # # Convert keypoints to a numpy array for consistency
        # self.prev_features = np.array([kp.pt for kp in keypoints], dtype=np.float32).reshape(-1, 1, 2)

        # Assign unique IDs to each detected microsphere
        self.microsphere_ids = [self.next_particle_id + i for i in range(len(self.prev_features))]
        self.next_particle_id += len(self.prev_features)  # Increment the ID counter

        # Create a debug frame to keep annotations from all detections
        debug_annotated_frame = current_frame.copy()

        # Filter features within bounds
        frame_height, frame_width = gray.shape[:2]
        # Process each detected feature to calculate its size
        valid_features = []  # List to store features with non-zero sizes
        valid_ids = []  # List to store IDs of features with non-zero sizes

        # Calculate the size of each microsphere (assuming circular features)
        for i, feature in enumerate(self.prev_features):
            x, y = feature.ravel()
            # Ensure coordinates are within image bounds
            if 0 <= x < frame_width and 0 <= y < frame_height:

                size = self.calculate_size(gray, (x, y), self.microsphere_ids[i])

                # Validate the size result
                if size is not None and size > 0:  # Skip features with invalid or non-positive sizes
                    self.microsphere_sizes[self.microsphere_ids[i]] = size
                    self.trajectories[self.microsphere_ids[i]] = [(x, y)]
                    valid_features.append(feature)
                    valid_ids.append(self.microsphere_ids[i])

                    # Draw detection for debugging
                    if self.debug:
                        cv2.circle(debug_annotated_frame, (int(x), int(y)), 3, (0, 255, 0), -1)
                        cv2.putText(debug_annotated_frame,
                                    f"ID:{self.microsphere_ids[i]}",
                                    (int(x) + 5, int(y) - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.4,
                                    (0, 255, 0),
                                    1)

        # Update features with only valid ones
        if valid_features:
            self.prev_features = np.array(valid_features, dtype=np.float32).reshape(-1, 1, 2)
            self.microsphere_ids = valid_ids
        else:
            self.prev_features = None
            self.microsphere_ids = []

        self.prev_gray = gray

        # Show debug frame if enabled
        if self.debug:
            cv2.imshow("Detected Particles", debug_annotated_frame)
            cv2.waitKey(1)
        #     self.microsphere_sizes[self.microsphere_ids[i]] = size
        #     self.trajectories[self.microsphere_ids[i]] = [(x, y)]  # Initialize trajectory with the first position
        #
        #     valid_features.append(feature)  # Add feature to valid list
        #     valid_ids.append(self.microsphere_ids[i])  # Add ID to valid list
        #
        # # Update only valid features and IDs
        # self.prev_features = np.array(valid_features, dtype=np.float32).reshape(-1, 1, 2)
        # self.microsphere_ids = valid_ids
        # self.prev_gray = gray  # Store the processed grayscale frame for tracking

    def _preprocess_image(self, frame):
        """
        Preprocesses the image for both size calculation and annotation.
        Returns: processed image, contours, frame dimensions
        """

        # Display the original image for debugging
        if self.debug:
            cv2.imshow("Original Image", frame)
            cv2.waitKey(0)

        # Check if the image is already grayscale
        if len(frame.shape) == 2:  # Grayscale image
            gray = frame
        elif frame.shape[2] == 1:
            gray = frame
        else:  # Convert to grayscale if it's not already.
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        if self.debug:
            cv2.imshow("CLAHE Enhanced", enhanced)
            cv2.waitKey(0)

        # # Denoise
        # denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
        #
        # if self.debug:
        #     cv2.imshow("Denoised", denoised)
        #     cv2.waitKey(0)

        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)

        if self.debug:
            cv2.imshow("Blurred", blurred)
            cv2.waitKey(0)

        # Otsu's thresholding with additional processing
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        if self.debug:
            cv2.imshow("Binary", binary)
            cv2.waitKey(0)

        # Invert the binary image to make particles white and background black
        inverted_binary = cv2.bitwise_not(binary)

        if self.debug:
            cv2.imshow("Inverted Binary", inverted_binary)
            cv2.waitKey(0)
        #
        # # Morphological operations to clean up the binary image
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        # cleaned = cv2.morphologyEx(inverted_binary, cv2.MORPH_CLOSE, kernel, iterations=2)
        # cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
        #
        # if self.debug:
        #     cv2.imshow("Cleaned", cleaned)
        #     cv2.waitKey(0)

        # # --- Watershed Segmentation ---
        # # Ensure the image is binary (0 or 255) for watershed.
        # ret, sure_fg = cv2.threshold(cleaned, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        #
        # # Finding sure background area
        # sure_bg = cv2.dilate(sure_fg, kernel, iterations=3)  # Adjust iterations as needed
        #
        # # Finding unknown region
        # unknown = cv2.subtract(sure_bg, sure_fg)
        #
        # # Marker labelling
        # ret, markers = cv2.connectedComponents(sure_fg)
        #
        # # Add one to all labels so that sure background is not 0, but 1
        # markers = markers + 1
        #
        # # Now, mark the region of unknown with zero
        # markers[unknown == 255] = 0
        #
        # # Apply watershed
        # markers = cv2.watershed(frame, markers)  # Use frame for color visualization
        #
        contours, _ = cv2.findContours(inverted_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if self.debug:
            debug_contours_frame = frame.copy()
            # Display the contours for debugging
            cv2.drawContours(debug_contours_frame, contours, -1, (0, 0, 255), 1)
            cv2.imshow("Debug Contours", debug_contours_frame)
            cv2.waitKey(0)

        frame_height, frame_width = frame.shape[:2]
        return contours, frame_width, frame_height

    def _check_collision(self, x1, y1, size1, pos2):
        """Checks if two bounding boxes overlap."""
        x2, y2, size2 = pos2
        return x1 < x2 + size2[0] and x1 + size1[0] > x2 and y1 < y2 + size2[1] and y1 + size1[1] > y2

    def annotate_frame_with_ids(self, frame):
        """
        Annotate the frame with microsphere IDs and draw circles around the contours of the particles.

        :param frame: The input frame (image).
        :return: Annotated frame.
        """
        contours, frame_width, frame_height = self._preprocess_image(frame)  # Get the preprocessed results

        # Prepare list to store IDs associated with contours
        contour_ids = []
        text_positions = []  # Store the positions of already drawn text

        for i, contour in enumerate(contours):
            # Skip contours partially outside the frame
            if not is_contour_within_bounds(contour, frame_width, frame_height):
                continue  # Exclude particles outside the frame

            if len(contour) >= 5:
                ellipse = cv2.fitEllipse(contour)
                (cx, cy), (major_axis, minor_axis), angle = ellipse
                diameter = (major_axis + minor_axis) / 2
                # Assign a unique ID to this contour
                if i < len(self.microsphere_ids):  # Use existing ids if available
                    microsphere_id = self.microsphere_ids[i]

                else:
                    microsphere_id = self.next_particle_id
                    self.next_particle_id += 1  # Generate a new ID if needed
                # Store the ID associated with this contour
                contour_ids.append(microsphere_id)
                cv2.drawContours(frame, [contour], -1, (0, 255, 0), 1)
                cv2.ellipse(frame, ellipse, (0, 0, 255), 1)

                # --- Collision Detection ---
                text_size, _ = cv2.getTextSize(str(microsphere_id), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                text_x = int(cx - text_size[0] / 2)
                text_y = int(cy + text_size[1] / 2)  # Initial position

                # Check for collisions with previously drawn text
                while any(self._check_collision(text_x, text_y, text_size, pos) for pos in text_positions):
                    text_y += text_size[1] + 2  # Move text down

                text_positions.append((text_x, text_y, text_size))  # Store position

                # --- Boundary Check (after collision check) ---
                text_x = max(0, min(text_x, frame_width - text_size[0]))
                text_y = max(text_size[1], min(text_y, frame_height))  # consider text height

                cv2.putText(frame, str(microsphere_id), (text_x - 15, text_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        # Update microsphere_ids to reflect only the contours found and labeled in this frame
        self.microsphere_ids = contour_ids
    #
    #     # # Add trajectory rendering for tracked particles (if `trajectories` exist)
    #     # for particle_id, trajectory in self.trajectories.items():
    #     #     if len(trajectory) > 1:  # Render only if trajectory has at least two points
    #     #         for j in range(1, len(trajectory)):
    #     #             # Get consecutive points in the trajectory
    #     #             x1, y1 = int(trajectory[j - 1][0] * self.scaling_factor), int(
    #     #                 trajectory[j - 1][1] * self.scaling_factor)
    #     #             x2, y2 = int(trajectory[j][0] * self.scaling_factor), int(
    #     #                 trajectory[j][1] * self.scaling_factor)
    #     #
    #     #             # Draw trajectory as yellow line
    #     #             cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
    #     #
    #     #         # Annotate the particle ID at the last known position
    #     #         x_last, y_last = int(trajectory[-1][0] * self.scaling_factor), int(
    #     #             trajectory[-1][1] * self.scaling_factor)
    #     #         cv2.putText(frame, str(particle_id), (x_last + 5, y_last - 5),
    #     #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)  # Yellow text for trajectory ID
        return frame

    def calculate_and_store_microsphere_data(self, frame):
        """
        Detect microspheres in the current frame, calculate their size and contours,
        and store the information in a dictionary for annotation.

        Args:
            frame: The current frame (image).

        Returns:
            A dictionary where each key is a microsphere ID and the value is a dictionary
            with 'size' and 'contour' of the microsphere.
        """
        contours, frame_width, frame_height = self._preprocess_image(frame.copy())

        microsphere_data = {}  # Dictionary to store detected microsphere information
        for i, contour in enumerate(contours):
            if len(contour) >= 5:  # Ensure there are enough points to fit an ellipse
                try:
                    ellipse = cv2.fitEllipse(contour)
                    (cx, cy), (major_axis, minor_axis), angle = ellipse
                    diameter = (major_axis + minor_axis) / 2  # Calculate equivalent diameter (size)

                    # Assign a unique ID to each contour
                    microsphere_id = self.next_particle_id
                    self.next_particle_id += 1  # Increment the ID counter for the next particle

                    # Store the size and contour in the dictionary
                    microsphere_data[microsphere_id] = {
                        "size": diameter,
                        "contour": contour
                    }

                    if self.debug:
                        # Draw the ellipse and contour
                        cv2.drawContours(frame, [contour], -1, (0, 255, 0), 1)
                        cv2.ellipse(frame, ellipse, (255, 0, 0), 1)
                        cv2.putText(frame,
                                    f"ID:{microsphere_id}, D:{diameter:.1f}px",
                                    (int(cx), int(cy)),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5,
                                    (0, 255, 0),
                                    1)
                except Exception as e:
                    # Handle cases where ellipse fitting fails
                    if self.debug:
                        print(f"Error processing contour {i}: {e}")
        return microsphere_data

    def annotate_frame_with_microsphere_data(self, frame, microsphere_data):
        """
        Annotate the current frame with microsphere IDs and contours using pre-stored data.

        Args:
            frame: The current frame (image).
            microsphere_data: A dictionary of microsphere data containing their 'size' and 'contour'.
        """
        annotated_frame = frame.copy()
        annotations = []

        for microsphere_id, data in microsphere_data.items():
            contour = data["contour"]
            size = data["size"]

            # Fit an ellipse to obtain center for annotation
            if len(contour) >= 5:
                ellipse = cv2.fitEllipse(contour)
                (cx, cy), _, _ = ellipse
                # Draw the contour and ellipse on the frame
                cv2.drawContours(frame, [contour], -1, (0, 255, 0), 1)

                if self.debug:

                    cv2.ellipse(frame, ellipse, (255, 0, 0), 1)

                # Annotate with Microsphere ID and size
                # cv2.putText(frame,
                #             f"ID:{microsphere_id}",
                #             (int(cx) + 7, int(cy)),
                #             cv2.FONT_HERSHEY_SIMPLEX,
                #             0.5,
                #             (0, 255, 0),
                #             1)
        return frame

    def calculate_size(self, current_frame, position, microsphere_id):
        """
        Calculate the size of a microsphere located at a given position.

        :param current_frame: Current image/frame with detected particles.
        :param position: Tuple (x, y) of the detected feature coordinates.
        :param microsphere_id: ID of the particle
        :return: Measured diameter (in pixels) of the microsphere or 0 if calculation fails.
        """
        # Extract coordinates of the feature
        x, y = int(position[0]), int(position[1])

        contours, frame_width, frame_height = self._preprocess_image(current_frame)  # Get the preprocessed results

        # Find the contour containing the feature point
        selected_contour = None
        min_distance = float("inf")

        for contour in contours:
            # Check if point is inside or near contour
            dist = abs(cv2.pointPolygonTest(contour, (x, y), True))
            # Consider only contours that contain or are very close to the point, and choose the nearest one.
            if dist < min_distance and cv2.pointPolygonTest(contour, (x, y),
                                                            False) >= 0:  # Point inside or very near the edge
                min_distance = dist
                selected_contour = contour

        if selected_contour is None:
            if self.debug:
                print(f"No valid contour found for feature at ({x}, {y})")
            return None

        # Fit an ellipse to get more accurate size measurement
        if len(selected_contour) >= 5:
            try:
                ellipse = cv2.fitEllipse(selected_contour)
                (cx, cy), (major_axis, minor_axis), angle = ellipse

                # Calculate equivalent diameter
                diameter = (major_axis + minor_axis) / 2

                if self.debug:
                    # Draw the contour and ellipse
                    cv2.drawContours(current_frame, [selected_contour], -1, (0, 255, 0), 1)
                    cv2.ellipse(current_frame, ellipse, (255, 0, 0), 1)
                    cv2.putText(current_frame,
                                f"ID:{microsphere_id}, D:{diameter:.1f}px",
                                (int(cx), int(cy)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0),
                                1)
                # print(f"Calculated size for ID {microsphere_id}: {diameter:.1f}px")
                return diameter
            except:
                # Fallback to contour area if ellipse fitting fails
                area = cv2.contourArea(selected_contour)
                if area > 0:
                    diameter = 2 * np.sqrt(area / np.pi)
                    return diameter

        return None
    # def calculate_size(self, current_frame, position, microsphere_id=None):
    #     """
    #     Calculate the size of a microsphere located at a given position.
    #
    #     :param current_frame: Current image/frame with detected particles.
    #     :param position: Tuple (x, y) of the detected feature coordinates.
    #     :param microsphere_id: ID of the particle
    #     :return: Measured diameter (in pixels) of the microsphere or 0 if calculation fails.
    #     """
    #     # Extract coordinates of the feature
    #     x, y = int(position[0]), int(position[1])
    #
    #     contours, frame_width, frame_height = self._preprocess_image(current_frame.copy())  # Get the preprocessed results
    #
    #     # Find the contour containing the feature point
    #     selected_contour = None
    #     min_distance = float("inf")
    #
    #     for contour in contours:
    #         # Check if point is inside or near contour
    #         dist = abs(cv2.pointPolygonTest(contour, (x, y), True))
    #         # Consider only contours that contain or are very close to the point, and choose the nearest one.
    #         if dist < min_distance and cv2.pointPolygonTest(contour, (x, y),
    #                                                     False) >= 0:  # Point inside or very near the edge
    #             min_distance = dist
    #             selected_contour = contour
    #
    #     if selected_contour is None:
    #         if self.debug:
    #             print(f"No valid contour found for feature at ({x}, {y})")
    #         return None
    #
    #     # Fit an ellipse to get more accurate size measurement
    #     if len(selected_contour) >= 5:
    #         try:
    #             ellipse = cv2.fitEllipse(selected_contour)
    #             (cx, cy), (major_axis, minor_axis), angle = ellipse
    #
    #             # Calculate equivalent diameter
    #             diameter = (major_axis + minor_axis) / 2
    #
    #             if self.debug:
    #                 # Draw the contour and ellipse
    #                 cv2.drawContours(current_frame, [selected_contour], -1, (0, 255, 0), 1)
    #                 cv2.ellipse(current_frame, ellipse, (255, 0, 0), 1)
    #                 cv2.putText(current_frame,
    #                             f"ID:{microsphere_id}, D:{diameter:.1f}px",
    #                             (int(cx), int(cy)),
    #                             cv2.FONT_HERSHEY_SIMPLEX,
    #                             0.5,
    #                             (0, 255, 0),
    #                             1)
    #             # print(f"Calculated size for ID {microsphere_id}: {diameter:.1f}px")
    #             return diameter
    #         except:
    #             # Fallback to contour area if ellipse fitting fails
    #             area = cv2.contourArea(selected_contour)
    #             if area > 0:
    #                 diameter = 2 * np.sqrt(area / np.pi)
    #                 return diameter
    #
    #     return None # Return None if no suitable contour is found.

    def calculate_velocity(self, new_x, new_y, old_x, old_y):
        """Calculate velocity from trajectory and frame rate."""
        dx = new_x - old_x
        dy = new_y - old_y

        # Calculate distance in pixels
        distance_pixels = np.sqrt(dx ** 2 + dy ** 2)

        # Velocity in pixels per second
        velocity = distance_pixels * self.fps

        return velocity

    # def perform_metrology_calculations(self, frame):
    #     """Performs metrology calculations: feature detection, tracking, and measurements."""
    #
    #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(
    #         frame.shape) > 2 else frame  # Simplified grayscale conversion.
    #
    #     if self.prev_gray is None:
    #         self.prev_gray = gray
    #         self.initialize_features(frame.copy(), False)  # Initialize ONLY when self.prev_gray is None
    #         return []  # return empty list initially
    #
    #     p1, st, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, gray, self.prev_features, None, **self.lk_params)
    #
    #     results = []  # Initialize results
    #
    #     if p1 is not None:
    #         good_new = p1[st == 1]
    #         good_old = self.prev_features[st == 1]
    #
    #         # Handle if features are lost
    #         if not good_new.any() or not good_old.any():
    #             print("All features lost. Re-initializing.")
    #             self.prev_gray = None  # Clear previous frame to trigger re-initialization on next call.
    #             self.prev_features = None  # Clear features.
    #             self.initialize_features(frame, True)  # Re-initialize
    #             return []  # return empty list after re-initialization.
    #
    #         new_id_mapping = {}  # Initialize id_mapping locally, within the function.
    #         updated_trajectories = {}  # Initialize trajectories.
    #
    #         for new, old in zip(good_new, good_old):
    #             a, b = new.ravel()
    #             c, d = old.ravel()
    #
    #             old_tuple = tuple(old.flatten())
    #
    #             particle_id = self.id_mapping.get(old_tuple)  # Get particle_id for old coordinates
    #
    #             if particle_id is None:  # Assign new ID if not found
    #                 particle_id = self.next_particle_id
    #                 self.next_particle_id += 1  # Increment next available ID
    #                 if particle_id >= len(self.colors):  # Access colors as part of the class.
    #                     self.colors.append(
    #                         self.get_random_color())
    #
    #
    #             size = self.calculate_size(gray, new, particle_id)  # Calculate size using new coordinates.
    #
    #             if size is not None:
    #                 self.microsphere_sizes[particle_id] = size
    #                 size_um = (size / self.scaling_factor) * 1000
    #                 velocity = self.calculate_velocity(a, b, c, d)  # Calculate velocity
    #                 velocity_mm_per_s = velocity / self.scaling_factor
    #
    #                 new_id_mapping[tuple(new.flatten())] = particle_id  # Update id mapping with NEW coordinates.
    #                 self.trajectories.setdefault(particle_id, []).append(
    #                     (a, b))  # Update trajectories with NEW coordinates.
    #
    #                 x_mm = a / self.scaling_factor
    #                 y_mm = b / self.scaling_factor
    #                 trajectory_mm = []
    #                 if particle_id in updated_trajectories:  # Use updated_trajectories
    #                     for x, y in updated_trajectories[particle_id]:
    #                         trajectory_mm.append((x / self.scaling_factor, y / self.scaling_factor))
    #                 results.append({  # Append the result directly
    #                     "frame_number": self.frame_number,
    #                     "particle_id": particle_id,
    #                     "x": x_mm,
    #                     "y": y_mm,
    #                     "size": size_um,
    #                     "velocity": velocity_mm_per_s,
    #                     "trajectory": trajectory_mm
    #                 })
    #
    #         self.trajectories = updated_trajectories  # Update the module-level trajectories.
    #         self.id_mapping = new_id_mapping
    #
    #         self.prev_features = good_new.reshape(-1, 1, 2)
    #         self.frame_number += 1
    #
    #     self.prev_gray = gray.copy()
    #     return results

    # def perform_metrology_calculations(self, frame, trajectories, scaling_factor, id_mapping):
    #     """Performs metrology calculations on a single frame, suitable for multiprocessing."""
    #     # Check if the image is already grayscale
    #     if len(frame.shape) == 2:  # Grayscale image
    #         gray = frame
    #     elif frame.shape[2] == 1:  # Single channel image
    #         gray = frame
    #     else:  # Convert to grayscale if it's not already
    #         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #
    #     if self.prev_gray is None:
    #         self.prev_gray = gray
    #         self.initialize_features(frame.copy(), False)  # Initialize features (lk_params, feature_params, prev_features)
    #         return  # Skip calculations on the very first frame
    #
    #     p1, st, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, gray, self.prev_features, None, **self.lk_params)
    #
    #     if p1 is not None:
    #         good_new = p1[st == 1]
    #         good_old = self.prev_features[st == 1]
    #
    #         if not good_new.any() or not good_old.any():  # Check if all features are lost
    #             self.initialize_features(gray.copy(), True)  # Re-initialize features here
    #             self.prev_gray = gray.copy()  # Update prev_gray with the re-initialized features' frame
    #             return []
    #
    #         results = []  # Store results for the current frame.
    #
    #         for new, old in zip(good_new, good_old):
    #             a, b = new.ravel()
    #             c, d = old.ravel()
    #
    #             particle_id = id_mapping.get(tuple(old.flatten()))
    #
    #             if particle_id is not None:  # Process only if particle_id found
    #                 size = self.calculate_size(gray.copy(), new, particle_id)
    #
    #                 if size is not None:  # Log only if size calculation was successful
    #
    #                     size_um = (size / scaling_factor) * 1000
    #                     velocity = self.calculate_velocity(a, b, c, d)
    #                     velocity_mm_per_s = velocity / scaling_factor
    #                     x_mm = a / scaling_factor
    #                     y_mm = b / scaling_factor
    #                     trajectory_mm = []
    #                     if particle_id in trajectories:
    #                         for x, y in trajectories[particle_id]:
    #                             trajectory_mm.append((x / scaling_factor, y / scaling_factor))
    #
    #                     self.microsphere_velocities[particle_id] = velocity  # store velocity
    #                     self.microsphere_sizes[particle_id] = size
    #
    #                     results.append({
    #                         "frame_number": self.frame_number,
    #                         "particle_id": particle_id,
    #                         "x": x_mm,
    #                         "y": y_mm,
    #                         "size": size_um,
    #                         "velocity": velocity_mm_per_s,
    #                         "trajectory": trajectory_mm
    #                     })
    #         self.prev_features = good_new.reshape(-1, 1, 2)
    #
    #     else:
    #         self.initialize_features(gray.copy(), True)  # Re-initialize features
    #         self.prev_gray = gray.copy()  # Update prev_gray to reflect changes
    #         return []
    #
    #     self.prev_gray = gray.copy()
    #     return results

    def annotate_frame(self, frame):
        """Annotates the frame with particle IDs and trajectories."""
        for particle_id in self.microsphere_ids:  # Iterate through tracked IDs
            if particle_id in self.microsphere_positions and self.microsphere_positions[particle_id]:
                x_mm, y_mm = self.microsphere_positions[particle_id][-1]  # Last position
                x = int(x_mm * self.scaling_factor)
                y = int(y_mm * self.scaling_factor)
                cv2.putText(frame, str(particle_id), (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Draw trajectories (if available)
            if particle_id in self.trajectories and len(self.trajectories[particle_id]) > 1:
                trajectory = self.trajectories[particle_id]
                for i in range(1, len(trajectory)):  # Draw lines between consecutive points
                    x1, y1 = int(trajectory[i - 1][0] * self.scaling_factor), int(
                        trajectory[i - 1][1] * self.scaling_factor)
                    x2, y2 = int(trajectory[i][0] * self.scaling_factor), int(trajectory[i][1] * self.scaling_factor)
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 1)  # Yellow line for trajectory

        return frame

    def detect_new_particles(self, current_frame):
        """
        Detect new microspheres in the current frame and avoid duplicates.
        """
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        # Detect new features (good features to track)
        new_features = cv2.goodFeaturesToTrack(
            gray,
            maxCorners=2000,
            qualityLevel=0.03,
            minDistance=1,
            blockSize=3
        )

        if new_features is not None:
            for feature in new_features:
                x, y = feature.ravel()
                is_duplicate = False

                # Check if this new feature overlaps with an existing one
                for existing_feature in self.prev_features:
                    ex, ey = existing_feature.ravel()
                    if np.sqrt((x - ex) ** 2 + (y - ey) ** 2) < 15:  # Distance threshold for duplicates
                        is_duplicate = True
                        break

                if not is_duplicate:
                    # Generate a new ID for this particle
                    new_id = self.next_particle_id
                    self.next_particle_id += 1  # Increment ID counter

                    size = self.calculate_size(gray, self.persistent_debug_frame, (x, y), new_id)

                    if size is not None:
                        # Convert size to microns
                        size_um = (size / self.scaling_factor) * 1000
                    else:
                        size_um = 0  # Or another appropriate default value, maybe logging a warning
                        if self.debug:
                            print(f"Warning: Size is None for particle {new_id}")

                    # Save the new feature
                    # Reshape new feature to (1, 1, 2) and ensure float32 type
                    new_feature = np.array([[[x, y]]], dtype=np.float32)
                    self.prev_features = np.vstack([self.prev_features, new_feature])
                    self.microsphere_ids.append(new_id)
                    self.microsphere_sizes[new_id] = size if size is not None else 0
                    self.trajectories[new_id] = [(x / self.scaling_factor, y / self.scaling_factor)]  # Positions in mm

                    self.microsphere_positions[new_id] = [(x / self.scaling_factor, y / self.scaling_factor)]
                    self.microsphere_velocities[new_id] = []

                    # Log new particle data to CSV
                    self.log_to_csv(self.frame_number, new_id, x / self.scaling_factor,
                                    y / self.scaling_factor, size_um, 0,
                                    [(x / self.scaling_factor, y / self.scaling_factor)])

    def remove_lost_particles(self, lost_ids):
        """
        Remove particles that are no longer detected from trajectories and other tracking dictionaries.

        :param lost_ids: List of particle IDs that are no longer detected.
        """
        for particle_id in lost_ids:
            if particle_id in self.trajectories:
                del self.trajectories[particle_id]
            if particle_id in self.microsphere_positions:
                del self.microsphere_positions[particle_id]
            if particle_id in self.microsphere_velocities:
                del self.microsphere_velocities[particle_id]
            if particle_id in self.microsphere_sizes:
                del self.microsphere_sizes[particle_id]

    def validate_row(self, frame_number, timestamp, particle_id, x, y, size, velocity, trajectory):
        """
        Validate the values to ensure no invalid data is written to the CSV file.

        :param frame_number: Frame number.
        :param timestamp: Timestamp of the frame (in seconds).
        :param particle_id: Unique ID of the particle.
        :param x: X-coordinate in mm.
        :param y: Y-coordinate in mm.
        :param size: Size of the particle (in μm).
        :param velocity: Velocity of the particle (in mm/s).
        :param trajectory: List of trajectory coordinates (in mm).
        :return: True if the row is valid, otherwise False.
        """
        if frame_number is None or frame_number < 0:
            return False
        if timestamp is None or timestamp < 0:
            return False
        if particle_id is None or particle_id <= 0:
            return False
        if x is None or x <= 0:
            return False
        if y is None or y <= 0:
            return False
        if size is None or size <= 0:  # Size must be positive
            return False
        if velocity is None or velocity < 0:  # Velocity can be zero but not negative
            return False
        if not trajectory or not isinstance(trajectory, list):  # Trajectory must be a valid list
            return False

        # Additional checks can be added as needed
        return True


def is_contour_within_bounds(contour, frame_width, frame_height):
    """
    Check if a contour's bounding box is entirely within the frame boundaries.

    :param contour: Single contour to check.
    :param frame_width: Width of the frame.
    :param frame_height: Height of the frame.
    :return: True if the bounding box of the contour is fully inside bounds, otherwise False.
    """
    x, y, w, h = cv2.boundingRect(contour)

    # Ensure no part of the bounding box is outside the frame dimensions
    return x >= 0 and y >= 0 and (x + w) <= frame_width and (y + h) <= frame_height



# Size Calculation Improvements


    # if len(self.microsphere_sizes) > 0:
    #     # Estimate average particle size (update based on ground truth or past frames)
    #     average_size = np.mean([size for size in self.microsphere_sizes.values() if size > 0])
    #     # Define a region of interest around the feature
    #     roi_size = max(5, int(average_size // 3))
    # else:
    #     roi_size = 100

    # x1, x2 = max(0, x - roi_size), min(gray_frame.shape[1], x + roi_size)
    # y1, y2 = max(0, y - roi_size), min(gray_frame.shape[0], y + roi_size)
    # roi = gray_frame[y1:y2, x1:x2]

    # # Adaptive Thresholding for segmentation
    # threshold_image = cv2.adaptiveThreshold(
    #     gray_frame, 255,
    #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # Gaussian-weighted mean for thresholding
    #     cv2.THRESH_BINARY,
    #     blockSize=11,  # Local neighborhood size
    #     C=2  # Subtraction constant for fine-tuning
    # )

    # # Calculate contour area and perimeter
    # area = cv2.contourArea(contour)
    # perimeter = cv2.arcLength(contour, True)
    #
    # # # Filter out noise and irregular shapes
    # # if area < 1 or area > 1000:  # Adjust these thresholds based on your images
    # #     continue
    #
    # # Calculate circularity
    # circularity = 4 * np.pi * area / (perimeter * perimeter)
    # if circularity < 0.5:  # Filter non-circular objects
    #     continue

# # Initialize variables for selecting the appropriate contour
        # selected_contour = None
        # min_distance = float("inf")
        #
        # # Filter and select the closest contour containing the feature point
        # for contour in contours:
        #     # Determine if the feature point lies within the contour
        #     if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
        #         # Measure the distance from the center and contour area
        #         contour_area = cv2.contourArea(contour)
        #         # # Ignore unreasonably small or large contours
        #         if contour_area < 1 or contour_area > 1000:  # Fine-tune these limits
        #              continue
        #
        #         # Choose the contour closest to the feature point (to prioritize relevant regions)
        #         moments = cv2.moments(contour)
        #         cx = int(moments["m10"] / moments["m00"]) if moments["m00"] != 0 else x
        #         cy = int(moments["m01"] / moments["m00"]) if moments["m00"] != 0 else y
        #
        #         # Calculate distance between detected center and feature point
        #         distance = np.sqrt((cx - x) ** 2 + (cy - y) ** 2)
        #
        #         if distance < min_distance:
        #             min_distance = distance
        #             selected_contour = contour
        #
        # # If no suitable contour is found, return 0
        # if selected_contour is None:
        #     if self.debug:
        #         print(f"No valid contour found for feature at ({x}, {y}).")
        #     return 0
        #
        # # Fit an ellipse to the selected contour
        # if len(selected_contour) >= 5:  # At least 5 points are needed to fit an ellipse
        #     ellipse = cv2.fitEllipse(selected_contour)
        #     (cx, cy), (major_axis, minor_axis), angle = ellipse  # Fitted parameters
        #
        #     # Add optional visualization for debugging
        #     if self.debug:
        #         cv2.ellipse(current_frame, ellipse, (0, 255, 0), 2)  # Draw the fitted ellipse
        #         cv2.putText(
        #             current_frame,
        #             f"ID: {microsphere_id}",
        #             (int(cx) + 10, int(cy) - 10),
        #             cv2.FONT_HERSHEY_SIMPLEX,
        #             0.5,
        #             (0, 255, 0),
        #             1
        #         )
        #
        #     # Calculate the equivalent diameter (mean of major and minor axes)
        #     equivalent_diameter = (major_axis + minor_axis) / 2
        #
        # else:
        #     # Fallback to contour bounding box if ellipse fitting fails
        #     x, y, w, h = cv2.boundingRect(selected_contour)  # Bounding box
        #     equivalent_diameter = (w + h) / 2
        #
        #     # Debug visualization for bounding rectangle
        #     if self.debug:
        #         cv2.rectangle(current_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Draw the rectangle
        #         cv2.putText(
        #             current_frame,
        #             f"ID: {microsphere_id}",
        #             (x + 10, y - 10),
        #             cv2.FONT_HERSHEY_SIMPLEX,
        #             0.5,
        #             (255, 0, 0),
        #             1
        #         )
        #         cv2.imshow("Bounding Box Fallback (Debug)", current_frame)
        #         cv2.waitKey(0)
        #
        # return equivalent_diameter

    # # Function to calculate the size of a microsphere
    # def calculate_size(self, gray_frame, current_frame, position):
    #     # Use a circular region growing technique to estimate the size of the microsphere
    #     x, y = int(position[0]), int(position[1])
    #     # Image segmentation: Otsu's binarization by setting flag to cv2.THRESH_OTSU
    #     # Optimal threshold value is calculated automatically
    #     # otsu_threshold, threshold_image = cv2.threshold(gray_frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    #     # print("Obtained Otsu threshold: ", otsu_threshold)
    #
    #     # Adaptive thresholding for better segmentation of small/faint particles
    #     threshold_image = cv2.adaptiveThreshold(
    #         gray_frame, 255,
    #         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # Gaussian-weighted mean for adaptive thresholding
    #         cv2.THRESH_BINARY,
    #         blockSize=11,  # Size of the local region
    #         C=2  # Constant subtracted from the mean
    #     )
    #
    #     # Find contours in the thresholded image and store them in a list.
    #     contours, _ = cv2.findContours(threshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #
    #     if self.debug:
    #         # Display the thresholded image and contours for debugging
    #         debug_image = current_frame.copy()
    #         cv2.drawContours(debug_image, contours, -1, (255, 0, 0), 1)
    #
    #         # Threshold image and detected contours for debugging
    #         cv2.imshow("Threshold Image", threshold_image)  # Show the binary threshold result
    #         cv2.imshow("Contours on Image", gray_frame)  # Display contours and features on the image
    #         cv2.waitKey(0)  # Wait for a keypress before closing
    #         cv2.destroyAllWindows()
    #
    #     selected_contour = None
    #     max_area = 0
    #
    #     for contour in contours:
    #         # Only consider contours that enclose the feature position
    #         if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
    #             area = cv2.contourArea(contour)
    #             if area > max_area:  # Keep the largest valid contour
    #                 max_area = area
    #                 selected_contour = contour
    #
    #     # If no contour is found containing the feature, return 0
    #     if selected_contour is None:
    #         return 0
    #
    #     # Smooth the contour to reduce noise
    #     # epsilon = 0.01 * cv2.arcLength(selected_contour, True)
    #     # smoothed_contour = cv2.approxPolyDP(selected_contour, epsilon, True)
    #
    #     # Fit a minimum enclosing circle to the selected contour
    #     (_, _), radius = cv2.minEnclosingCircle(selected_contour)
    #
    #     # Optionally, draw the contour and circle on the image for debugging
    #     cv2.drawContours(current_frame, [selected_contour], -1, (255, 0, 0), 2)  # Draw contour in blue
    #     cv2.circle(current_frame, (x, y), int(radius), (0, 255, 0), 2)  # Draw circle in green
    #
    #     # Return the diameter of the circle (2 * radius)
    #     return radius * 2

        # # Loop over all contours to find the best match
        # for contour in contours:
        #     if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
        #         area = cv2.contourArea(contour)
        #         if area > max_area:  # Keep the largest valid contour
        #             max_area = area
        #             selected_contour = contour
        #
        # # If no contour is found containing the feature, return 0
        # if selected_contour is None:
        #     return 0
        #
        #         # Draw the contour around the detected microsphere
        #         cv2.drawContours(current_frame, [contour], -1, (255, 0, 0), 3)
        #         epsilon = 0.01 * cv2.arcLength(contour, True)  # Approximation parameter
        #         contour = cv2.approxPolyDP(contour, epsilon, True)
        #
        #         # Calculate the radius of the minimum enclosing circle
        #         (_, _), radius = cv2.minEnclosingCircle(contour)
        #         return radius * 2  # Diameter of the microsphere
        #     return 0

    # """
    #         Process the current frame to calculate velocities and sizes,
    #         and write data to the CSV file.
    #         """
    # # Increment the frame number
    # self.frame_number += 1
    #
    # # If previous frame or features are not initialized, initialize them
    # if self.prev_gray is None:
    #     # Initialize tracking features on the first frame
    #     self.initialize_features(frame, False)
    #     self.prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #     return
    #
    # # Convert the current frame to grayscale
    # current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #
    # # Check if previous features exist before calculating optical flow
    # if self.prev_features is None or self.prev_features.size == 0:
    #     self.prev_features = cv2.goodFeaturesToTrack(
    #         current_gray,
    #         maxCorners=2000,
    #         qualityLevel=0.01,
    #         minDistance=5,
    #         blockSize=5,
    #         useHarrisDetector=True,
    #         k=0.04
    #     )
    #     # Refine features to subpixel accuracy
    #     criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    #     self.prev_features = cv2.cornerSubPix(
    #         current_gray,
    #         self.prev_features,
    #         winSize=(5, 5),  # Search window size
    #         zeroZone=(-1, -1),
    #         criteria=criteria
    #     )
    #     self.prev_gray = current_gray  # Update previous frame
    #     return  # Return to ensure that the code processes in next iteration with initialized features
    #
    # # Calculate optical flow using Lucas-Kanade method
    # current_features, status, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, current_gray, self.prev_features, None,
    #                                                          **self.lk_params)
    #
    # if current_features is None:  # handle the case when no features are found
    #     self.prev_features = cv2.goodFeaturesToTrack(
    #         current_gray,
    #         maxCorners=2000,
    #         qualityLevel=0.01,
    #         minDistance=5,
    #         blockSize=7  # Increased block size for better feature detection
    #     )
    #     self.prev_gray = current_gray
    #     return
    #
    # updated_features = []
    # updated_ids = []
    # lost_ids = []  # Keep track of particle IDs that are lost
    #
    # print(f"Frame {self.frame_number}:")  # Debug output
    #
    # # Match previous features to current frame features
    # for i, (prev, curr) in enumerate(zip(self.prev_features, current_features)):
    #     if status[i] == 1 and err[i] < 50:  # Status 1 means that the feature point was found in both frames,
    #         # and err[i] is within acceptable range
    #
    #         microsphere_id = self.microsphere_ids[i]
    #         x_mm = curr[0][0] / self.scaling_factor  # Convert x-coordinate to mm
    #         y_mm = curr[0][1] / self.scaling_factor  # Convert y-coordinate to mm
    #
    #         # Calculate the displacement in x and y directions
    #         dx = curr[0][0] - prev[0][0]
    #         dy = curr[0][1] - prev[0][1]
    #
    #         # Calculate velocity using the separate function
    #         velocity_mm_s = self.calculate_velocity(dx, dy)
    #
    #         # Update positions and velocities
    #         if microsphere_id not in self.microsphere_positions:
    #             self.microsphere_positions[microsphere_id] = []
    #         if microsphere_id not in self.microsphere_velocities:
    #             self.microsphere_velocities[microsphere_id] = []
    #
    #         self.microsphere_positions[microsphere_id].append((x_mm, y_mm))
    #         self.microsphere_velocities[microsphere_id].append(velocity_mm_s)
    #
    #         # Update the trajectory
    #         if microsphere_id in self.trajectories:
    #             self.trajectories[microsphere_id].append((x_mm, y_mm))
    #         else:
    #             self.trajectories[microsphere_id] = [(x_mm, y_mm)]
    #
    #         # Log the data to CSV
    #         trajectory_mm = [(x / self.scaling_factor, y / self.scaling_factor) for x, y in
    #                          self.trajectories[microsphere_id]]
    #         self.log_to_csv(self.frame_number, microsphere_id, x_mm, y_mm,
    #                         self.microsphere_sizes.get(microsphere_id, 0), velocity_mm_s, trajectory_mm)
    #
    #         # Keep track of updated features and IDs
    #         updated_features.append(curr)
    #         updated_ids.append(microsphere_id)
    #     else:
    #         # If particle is lost, add its ID to the lost list ONLY if i is within range
    #         if i < len(self.microsphere_ids):  # Check if the index is valid
    #             lost_ids.append(self.microsphere_ids[i])
    #
    # # Remove trajectories of lost particles
    # self.remove_lost_particles(lost_ids)
    #
    # # Update previous frame and features for the next iteration
    # self.prev_gray = current_gray
    # self.prev_features = np.array(updated_features, dtype=np.float32)
    # self.microsphere_ids = updated_ids
    #
    # # Detect new features and add them if they don't overlap with existing ones
    # self.detect_new_particles(frame)