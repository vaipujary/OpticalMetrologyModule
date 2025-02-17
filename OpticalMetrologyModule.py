import cv2
import numpy as np
import matplotlib.pyplot as plt
import logging
import trackpy as tp
import pims
import skimage as ski

# 355-425 um

class OpticalMetrologyModule:
    def __init__(self, debug=False):
        # Initialize previous frame and features to None
        self.prev_gray = None
        self.prev_features = None
        self.microsphere_ids = []
        self.microsphere_sizes = {}  # Dictionary to store the size of each microsphere
        self.trajectories = {}  # Dictionary to store trajectories of each microsphere
        self.frame_number = 0  # Keep track of the current frame number
        # Parameters for Lucas-Kanade optical flow
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.debug = debug
        self.persistent_debug_frame = None

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
        # Convert frame to grayscale
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

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
        #

        # Assign unique IDs to each detected microsphere
        self.microsphere_ids = [f"{self.frame_number}-{i}" for i in range(len(self.prev_features))]

        # Create a debug frame to keep annotations from all detections
        debug_annotated_frame = current_frame.copy()

        # Process each detected feature to calculate its size
        valid_features = []  # List to store features with non-zero sizes
        valid_ids = []  # List to store IDs of features with non-zero sizes

        # Calculate the size of each microsphere (assuming circular features)
        for i, feature in enumerate(self.prev_features):
            x, y = feature.ravel()
            # Ensure coordinates are within image bounds
            if 0 <= x < gray.shape[1] and 0 <= y < gray.shape[0]:

                size = self.calculate_size(gray, self.persistent_debug_frame, (x, y), self.microsphere_ids[i])

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

    def annotate_frame_with_ids(self, frame):
        """
        Annotate the frame with microsphere IDs and draw circles around the contours of the particles.

        :param frame: The input frame (image).
        :return: Annotated frame.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
        blurred = cv2.GaussianBlur(denoised, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        inverted_binary = cv2.bitwise_not(binary)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned = cv2.morphologyEx(inverted_binary, cv2.MORPH_CLOSE, kernel, iterations=2)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for i, contour in enumerate(contours):
            if len(contour) >= 5:
                ellipse = cv2.fitEllipse(contour)
                (cx, cy), (major_axis, minor_axis), angle = ellipse
                diameter = (major_axis + minor_axis) / 2
                microsphere_id = self.microsphere_ids[i] if i < len(self.microsphere_ids) else f"unknown-{i}"
                cv2.drawContours(frame, [contour], -1, (0, 255, 0), 1)
                cv2.ellipse(frame, ellipse, (255, 0, 0), 1)
                cv2.putText(frame, str(microsphere_id), (int(cx) + 10, int(cy) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        return frame

    def calculate_size(self, gray_frame, current_frame, position, microsphere_id):
        """
        Calculate the size of a microsphere located at a given position.

        :param enhanced: Grayscale image for processing.
        :param current_frame: Current image/frame with detected particles.
        :param position: Tuple (x, y) of the detected feature coordinates.
        :return: Measured diameter (in pixels) of the microsphere or 0 if calculation fails.
        """
        # Extract coordinates of the feature
        x, y = int(position[0]), int(position[1])

        # Display the original image for debugging
        if self.debug:
            cv2.imshow("Original Image", gray_frame)
            cv2.waitKey(0)

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

        # Preprocess the image for better segmentation
        # 1. CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray_frame)

        if self.debug:
            cv2.imshow("CLAHE Enhanced", enhanced)
            cv2.waitKey(0)
        #
        # # 2. Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)

        if self.debug:
            cv2.imshow("Denoised", denoised)
            cv2.waitKey(0)

        # 3. Apply Gaussian blur
        blurred = cv2.GaussianBlur(denoised, (5, 5), 0)

        if self.debug:
            cv2.imshow("Denoised", denoised)
            cv2.waitKey(0)

        # # Adaptive Thresholding for segmentation
        # threshold_image = cv2.adaptiveThreshold(
        #     gray_frame, 255,
        #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # Gaussian-weighted mean for thresholding
        #     cv2.THRESH_BINARY,
        #     blockSize=11,  # Local neighborhood size
        #     C=2  # Subtraction constant for fine-tuning
        # )

        # 4. Otsu's thresholding with additional processing
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        if self.debug:
            cv2.imshow("Binary", binary)
            cv2.waitKey(0)

        # Invert the binary image to make particles white and background black
        inverted_binary = cv2.bitwise_not(binary)
        if self.debug:
            cv2.imshow("Inverted Binary", inverted_binary)
            cv2.waitKey(0)

        # 5. Morphological operations to clean up the binary image
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned = cv2.morphologyEx(inverted_binary, cv2.MORPH_CLOSE, kernel, iterations=2)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
        if self.debug:
            cv2.imshow("Cleaned", cleaned)
            cv2.waitKey(0)

        # Find contours
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the contour containing the feature point
        selected_contour = None
        min_distance = float('inf')

        if self.debug:
            debug_contours_frame = current_frame.copy()
            # Display the thresholded image and contours for debugging
            cv2.drawContours(debug_contours_frame, contours, -1, (0, 0, 255), 1)
            cv2.imshow("Debug Contours", debug_contours_frame)
            cv2.waitKey(0)

        selected_contour = None
        min_distance = float("inf")

        for contour in contours:
            # Calculate contour area and perimeter
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            # # Filter out noise and irregular shapes
            # if area < 1 or area > 1000:  # Adjust these thresholds based on your images
            #     continue

            # Calculate circularity
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < 0.5:  # Filter non-circular objects
                continue

            # Check if point is inside or near contour
            dist = cv2.pointPolygonTest(contour, (x, y), True)
            if dist >= -5:  # Accept points within or very close to contour
                if abs(dist) < min_distance:
                    min_distance = abs(dist)
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
                print(f"Calculated size for ID {microsphere_id}: {diameter:.1f}px")
                return diameter
            except:
                # Fallback to contour area if ellipse fitting fails
                area = cv2.contourArea(selected_contour)
                diameter = 2 * np.sqrt(area / np.pi)
                return diameter

        return None
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

    def process_frame_data(self, current_frame):
        # Increment the frame number
        self.frame_number += 1

        # If previous frame or features are not initialized, initialize them
        if self.prev_gray is None or self.prev_features is None:
            # Initialize tracking features on the first frame
            self.initialize_features(current_frame, False)
            return []

        # Convert the current frame to grayscale
        current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow using Lucas-Kanade method
        current_features, status, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, current_gray, self.prev_features, None,
                                                                 **self.lk_params)

        # Calculate velocities for each tracked feature
        microsphere_data = []
        updated_features = []
        updated_ids = []

        # Match previous features to current frame features
        for i, (prev, curr) in enumerate(zip(self.prev_features, current_features)):
            if status[i] == 1 and err[i] < 50:  # Status 1 means that the feature point was found in both frames,
                # and err[i] is within acceptable range
                # Calculate the displacement in x and y directions
                dx = curr[0][0] - prev[0][0]
                dy = curr[0][1] - prev[0][1]

                # Calculate the magnitude of velocity
                velocity = np.sqrt(dx ** 2 + dy ** 2)
                microsphere_id = self.microsphere_ids[i]

                microsphere_data.append({"id": microsphere_id,
                                         "velocity": velocity,
                                         "position": curr,
                                         "size": self.microsphere_sizes[microsphere_id]})

                # Update trajectory with the new position
                self.trajectories[microsphere_id].append((curr[0][0], curr[0][1]))

                updated_features.append(curr)
                updated_ids.append(microsphere_id)

        # Update previous frame and features for the next iteration
        self.prev_gray = current_gray
        self.prev_features = np.array(updated_features, dtype=np.float32)
        self.microsphere_ids = updated_ids

        # Detect new features and add them if they don't overlap with existing ones
        self.detect_new_particles(current_frame)

        return microsphere_data

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
                    new_id = f"{self.frame_number}-new-{len(self.microsphere_ids)}"
                    size = self.calculate_size(gray, self.persistent_debug_frame, (x, y), new_id)

                    # Save the new feature, ID, and size
                    self.prev_features = np.append(self.prev_features, [[x, y]], axis=0)
                    self.microsphere_ids.append(new_id)
                    self.microsphere_sizes[new_id] = size
                    self.trajectories[new_id] = [(x, y)]

                    # Annotate the new particle (optional for debug)
                    if self.debug:
                        cv2.circle(self.persistent_debug_frame, (int(x), int(y)), 5, (255, 0, 0), -1)
                        cv2.putText(self.persistent_debug_frame, new_id, (int(x) + 10, int(y) - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

