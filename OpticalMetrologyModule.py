import cv2
import numpy as np
import matplotlib.pyplot as plt
import logging
import trackpy as tp
import pims
import skimage as ski


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

    def initialize_features(self, current_frame, is_reduce_noise):
        # Convert frame to grayscale
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        if is_reduce_noise:
            current_frame = cv2.GaussianBlur(current_frame, (5, 5), 0)
        if self.debug:
            plt.imshow(current_frame)

        f = tp.locate(current_frame, 11, invert=False)

        if self.debug:
            f.head()
            tp.annotate(f, current_frame)

        # Detect good features to track using Shi-Tomasi corner detection
        self.prev_features = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
        # Assign unique IDs to each detected microsphere
        self.microsphere_ids = [f"{self.frame_number}-{i}" for i in range(len(self.prev_features))]
        # Calculate the size of each microsphere (assuming circular features)
        for i, feature in enumerate(self.prev_features):
            x, y = feature.ravel()
            size = self.calculate_size(gray, current_frame, (x, y))
            self.microsphere_sizes[self.microsphere_ids[i]] = size
            self.trajectories[self.microsphere_ids[i]] = [(x, y)]  # Initialize trajectory with the first position
        self.prev_gray = gray

        if self.debug:
            plt.imshow(current_frame)
            logging.debug(f"Initialized features: {self.microsphere_ids}")

    # Function to calculate the size of a microsphere
    @staticmethod
    def calculate_size(gray_frame, current_frame, position):
        # Use a circular region growing technique to estimate the size of the microsphere
        x, y = int(position[0]), int(position[1])
        # Image segmentation: Otsu's binarization by setting flag to cv2.THRESH_OTSU
        # Optimal threshold value is calculated automatically
        otsu_threshold, threshold_image = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        print("Obtained Otsu threshold: ", otsu_threshold)
        # Find contours in the thresholded image
        contours, hierarchy = cv2.findContours(threshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
                # Draw the contour around the detected microsphere
                cv2.drawContours(current_frame, [contour], -1, (0, 255, 0), 2)
                # Calculate the radius of the minimum enclosing circle
                (_, _), radius = cv2.minEnclosingCircle(contour)
                return radius * 2  # Diameter of the microsphere
            return 0

    def process_frame_data(self, current_frame):
        # Increment the frame number
        self.frame_number += 1

        # If previous frame or features are not initialized, initialize them
        if self.prev_gray is None or self.prev_features is None:
            # Initialize tracking features on the first frame
            self.initialize_features(current_frame)
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
        for i, (prev, curr) in enumerate(zip(self.prev_features, current_features)):
            if status[i] == 1 and err[i] < 50:  # Status 1 means that the feature point was found in both frames,
                # and err[i] is within acceptable range
                # Calculate the displacement in x and y directions
                dx = curr[0][0] - prev[0][0]
                dy = curr[0][1] - prev[0][1]
                # Calculate the magnitude of velocity
                velocity = np.sqrt(dx ** 2 + dy ** 2)
                microsphere_id = self.microsphere_ids[i]
                microsphere_data.append({"id": microsphere_id, "velocity": velocity, "position": curr,
                                   "size": self.microsphere_sizes[microsphere_id]})
                updated_features.append(curr)
                updated_ids.append(microsphere_id)
                # Update trajectory with the new position
                self.trajectories[microsphere_id].append((curr[0][0], curr[0][1]))

        # Update previous frame and features for the next iteration
        self.prev_gray = current_gray
        self.prev_features = np.array(updated_features, dtype=np.float32)
        self.microsphere_ids = updated_ids

        return microsphere_data
