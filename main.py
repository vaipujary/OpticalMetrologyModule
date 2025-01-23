import cv2
import time
import logging
import numpy as np
import pandas as pd
import random
import sys
import os
from OpticalMetrologyModule import OpticalMetrologyModule
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QTimer
from Custom_Widgets.Widgets import *
from mainWindow import *
from videoCalibration import *

# Set up logging configuration.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


########################################################################################
# MAIN WINDOW CLASS
########################################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.camera_dialog = VideoCalibrationDialog(self)

        # Video capture and output settings
        self.cam = cv2.VideoCapture('Test Data/Videos/3.mp4')  # Provide the path to your video
        self.fps = int(self.cam.get(cv2.CAP_PROP_FPS))
        # self.timer.start(int(1000 / self.fps))  # Set the timer interval to match video frame rate

        # Apply JSON stylesheet
        loadJsonStyle(self, self.ui)
        self.show()  # Show window

        # Expand center menu widget size
        self.ui.settingsBtn.clicked.connect(lambda:self.ui.centerMenuContainer.expandMenu())
        self.ui.infoBtn.clicked.connect(lambda: self.ui.centerMenuContainer.expandMenu())
        self.ui.helpBtn.clicked.connect(lambda: self.ui.centerMenuContainer.expandMenu())

        # Collapse center menu widget
        self.ui.closeCenterMenuBtn.clicked.connect(lambda: self.ui.centerMenuContainer.collapseMenu())

        # Expand right menu widget size
        self.ui.experimentControlsBtn.clicked.connect(lambda: self.ui.rightMenuContainer.expandMenu())
        self.ui.moreMenuBtn.clicked.connect(lambda: self.ui.rightMenuContainer.expandMenu())

        # Collapse right menu widget
        self.ui.closeRightMenuBtn.clicked.connect(lambda: self.ui.rightMenuContainer.collapseMenu())

        # Collapse notification widget
        self.ui.closeNotificationBtn.clicked.connect(lambda: self.ui.popupNotificationContainer.collapseMenu())

        self.ui.cameraBtn.clicked.connect(self.open_video_calibration_dialog)

    def open_video_calibration_dialog(self):
        # Show the dialog (modal, blocks interaction with the main window)
        self.camera_dialog.show()



class VideoCalibrationDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_VideoCalibrationDialog()
        self.ui.setupUi(self)

        # Initialize camera
        self.video_capture = cv2.VideoCapture(0)

        # Timer for video feed updates
        self.timer = None

        # Connect buttons
        self.ui.screenshotBtn.clicked.connect(self.capture_screenshot)
        self.ui.lineMeasurementBtn.clicked.connect(self.start_measurement)

        self.current_frame = None
        self.screenshot_captured = False
        self.measurement_started = False
        self.start_point = None
        self.end_point = None
        self.screenshot_pixmap = None

        # Enable mouse events on QLabel
        self.ui.videoLabel.setMouseTracking(True)

        # Start video feed
        #self.start_video_feed()

    def start_video_feed(self):
        self.timer = self.startTimer(6)  # Timer event updates every 6ms

    def timer_event(self, event):
        if not self.screenshot_captured:
            # Capture live feed frame
            ret, frame = self.video_capture.read()
            if ret:
                self.current_frame = frame
                self.display_frame(frame)

    def display_frame(self, frame):
        # Convert OpenCV BGR image to QImage
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.ui.videoLabel.setPixmap(pixmap)

    def capture_screenshot(self):
        if self.current_frame is not None:
            self.screenshot_captured = True  # Stop live feed
            self.killTimer(self.timer)  # Stop updating the video feed
            # Convert OpenCV frame to QPixmap
            rgb_image = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.screenshot_pixmap = QPixmap.fromImage(qt_image)
            self.ui.videoLabel.setPixmap(self.screenshot_pixmap)
            # Enable mouse event handling for drawing lines
            self.ui.videoLabel.mousePressEvent = self.select_point

    def start_measurement(self):
        """Start the measurement process when the button is clicked."""
        if not self.screenshot_captured:
            return  # User needs to capture the screenshot first
        self.measurement_started = True
        self.start_point = None
        self.end_point = None
        print("Measurement started. Select two points on the image.")

    def select_point(self, event):
        """Handle mouse click events for point selection."""
        if not self.measurement_started:
            return  # Do nothing if measurement has not been started

        if self.screenshot_captured:
            if self.start_point is None:
                # Store the first point
                self.start_point = event.pos()
                print(f"First Point Selected: ({self.start_point.x()}, {self.start_point.y()})")
            elif self.end_point is None:
                # Store the second point
                self.end_point = event.pos()
                print(f"Second Point Selected: ({self.end_point.x()}, {self.end_point.y()})")
                # Calculate distance and draw the result
                self.calculate_distance()


    def calculate_distance(self):
        if self.start_point and self.end_point:
            # Distance in pixels using Euclidean distance formula
            dx = self.end_point.x() - self.start_point.x()
            dy = self.end_point.y() - self.start_point.y()
            distance = (dx ** 2 + dy ** 2) ** 0.5
            print(f"Measured Distance: {distance:.2f} pixels")  # Log to console
            self.draw_line_and_points(distance)

    def draw_line_and_points(self, distance):
        # Draw the points and line on the captured screenshot
        pixmap = self.screenshot_pixmap.copy()
        painter = QPainter(pixmap)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen)

        # Draw line between the two points
        painter.drawLine(self.first_point, self.second_point)

        # Draw circles at the two points
        point_radius = 5
        painter.setBrush(Qt.red)
        painter.drawEllipse(self.first_point, point_radius, point_radius)
        painter.drawEllipse(self.second_point, point_radius, point_radius)

        # Add distance label
        painter.setPen(Qt.blue)
        painter.drawText(self.second_point, f"{distance:.2f} px")

        painter.end()
        self.ui.videoLabel.setPixmap(pixmap)

        # Reset points to allow a new measurement
        self.start_point = None
        self.end_point = None


class RealTimeVideoProcessor:
    def __init__(self, ui_video_label):
        self.ui_video_label = ui_video_label
        self.cam = cv2.VideoCapture('Test Data/Videos/3.mp4')
        #
        # if not self.cam.isOpened():
        #     print("Error: Could not open the ThorLabs camera.")
        # else:
        #     print("ThorLabs camera is open. Press 'q' to quit.")
        #     # Set desired FPS
        #     desired_fps = 30  # Replace with the desired FPS
        #     success = self.cam.set(cv2.CAP_PROP_FPS, desired_fps)
        #
        #     if success:
        #         print(f"Successfully set FPS to {desired_fps}.")
        #     else:
        #         print("Failed to set FPS. The camera may not support this setting.")
        #
        #     # Get and print the actual FPS to verify
        #     current_fps = self.cam.get(cv2.CAP_PROP_FPS)
        #     print(f"Camera is running at {current_fps} FPS.")
        # cv2.VideoCapture('Test Data/Videos/3.mp4')
        self.mask = None
        self.particle_colors = []
        self.trajectories = []
        self.old_gray = None
        self.p0 = None
        self.prev_frame_time = 0
        self.new_frame_time = 0
        # Parameters for goodFeaturesToTrack and Lucas-Kanade Optical Flow
        self.feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    def initialize_tracking(self):
        ret, old_frame = self.cam.read()
        if not ret:
            print("Error reading the video file.")
            return False
        self.old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask=None, **self.feature_params)
        if self.p0 is not None:
            # Assign a unique color to each particle based on its index
            self.particle_colors = {
                i: self.get_random_color() for i in range(len(self.p0))
            }
        self.mask = np.zeros_like(old_frame)
        return True
    @staticmethod
    def get_random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def process_frame(self):
        ret, frame = self.cam.read()
        if not ret:
            print("Video processing complete.")
            return None
        self.new_frame_time = time.time()
        fps = int(1 / (self.new_frame_time - self.prev_frame_time))
        self.prev_frame_time = self.new_frame_time

        # Draw FPS on the frame
        cv2.putText(frame, f"FPS: {fps}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 2, cv2.LINE_AA)

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow to get new positions of tracked points
        p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.p0, None, **self.lk_params)
        good_new = p1[st == 1] if p1 is not None else None
        good_old = self.p0[st == 1] if self.p0 is not None else None

        # If points are valid, update trajectories and draw uniform-colored lines
        if good_new is not None and good_old is not None:
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = int(new[0]), int(new[1])
                c, d = int(old[0]), int(old[1])

                # Draw the trajectory line in a single fixed color (e.g., green)
                fixed_color = (0, 255, 0)  # Green color for all trajectories
                self.mask = cv2.line(self.mask, (a, b), (c, d), fixed_color, 2)

                # Append points to trajectories for further usage/analysis
                if i >= len(self.trajectories):
                    self.trajectories.append([(a, b)])
                else:
                    self.trajectories[i].append((a, b))
                    # Trim trajectory length to at most 10 points
                    if len(self.trajectories[i]) > 10:
                        self.trajectories[i].pop(0)

        # Combine the original frame with the updated trajectory mask
        output = cv2.add(frame, self.mask)

        # Update the state for the next frame
        self.old_gray = frame_gray.copy()
        self.p0 = good_new.reshape(-1, 1, 2) if good_new is not None else None

        return output


def main():
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
        video_processor = RealTimeVideoProcessor(window.ui.videoFeedLabel)
        if not video_processor.initialize_tracking():
            sys.exit(1)
        window.show()

        # Process video frame by frame
        timer = QTimer()
        def update_video():
            processed_frame = video_processor.process_frame()
            if processed_frame is None:
                timer.stop()
                return
            # Get the size of the QLabel
            label_width = window.ui.videoFeedLabel.width()
            label_height = window.ui.videoFeedLabel.height()
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            resized_frame = cv2.resize(rgb_frame, (label_width, label_height), interpolation=cv2.INTER_AREA)
            qt_image = QImage(resized_frame.data, resized_frame.shape[1], resized_frame.shape[0], resized_frame.strides[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            window.ui.videoFeedLabel.setPixmap(pixmap)
        timer.timeout.connect(update_video)
        timer.start(6)
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()