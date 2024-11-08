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
        # Parameters for Lucas-Kanade optical flow
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.debug = debug

    def initialize_features(self, frame, is_reduce_noise):
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if is_reduce_noise:
            frame = cv2.GaussianBlur(frame, (5, 5), 0)

        if self.debug:
            plt.imshow(frame)

        f = tp.locate(frame, 11, invert=False)

        if self.debug:
            f.head()
            tp.annotate(f, frame)

        # Detect good features to track using Shi-Tomasi corner detection
        self.prev_features = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
        # Assign unique IDs to each detected microsphere
        self.microsphere_ids = list(range(len(self.prev_features)))
        # Calculate the size of each microsphere
        sizes = self.calculate_size(gray)
        for i, feature in enumerate(self.prev_features):
            x, y = feature.ravel()
            if i < len(sizes):
                self.microsphere_sizes[i] = sizes[i]
            self.trajectories[i] = [(x, y)]  # Initialize trajectory with the first position
            # Store the grayscale image for future use
        self.prev_gray = gray

        if self.debug:
            plt.imshow(frame)
            logging.debug(f"Initialized features: {self.microsphere_ids}")

    def calculate_size(self, gray_frame):
        # Image segmentation: Otsu's binarization by setting flag to cv2.THRESH_OTSU
        # Optimal threshold value is calculated automatically
        otsu_threshold, threshold_image = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        print("Obtained Otsu threshold: ", otsu_threshold)
        # Find contours in the thresholded image
        contours, _ = cv2.findContours(threshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        sizes = []

        for contour in contours:
            # Calculate the radius of the minimum enclosing circle
            (_, _), radius = cv2.minEnclosingCircle(contour)
            diameter = radius * 2  # Diameter of the microsphere
            sizes.append(diameter)

        return sizes

    def calculate_velocity(self, frame):
        # If previous frame or features are not initialized, initialize them
        if self.prev_gray is None or self.prev_features is None:
            # Initialize tracking features on the first frame
            self.initialize_features(frame)
            return []

        # Convert the current frame to grayscale
        current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow using Lucas-Kanade method
        current_features, status, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, current_gray, self.prev_features, None,
                                                                 **self.lk_params)

        # Calculate velocities for each tracked feature
        velocities = []
        updated_features = []
        updated_ids = []
        for i, (prev, curr) in enumerate(zip(self.prev_features, current_features)):
            if status[i] == 1:  # Status 1 means that the feature point was found in both frames
                # Calculate the displacement in x and y directions
                dx = curr[0][0] - prev[0][0]
                dy = curr[0][1] - prev[0][1]
                # Calculate the magnitude of velocity
                velocity = np.sqrt(dx ** 2 + dy ** 2)
                velocities.append({"id": self.microsphere_ids[i], "velocity": velocity, "position": curr})
                updated_features.append(curr)
                updated_ids.append(self.microsphere_ids[i])

        # Update previous frame and features for the next iteration
        self.prev_gray = current_gray
        self.prev_features = np.array(updated_features, dtype=np.float32)
        self.microsphere_ids = updated_ids

        return velocities
