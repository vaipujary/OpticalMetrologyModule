import json

import cv2
import time
import logging
import numpy as np
import pandas as pd
import random
import sys
import os
from OpticalMetrologyModule import OpticalMetrologyModule
from VideoProcessor import VideoProcessor
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QApplication, QFileDialog, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, QPointF
from Custom_Widgets.Widgets import *
from mainWindow import *
from videoCalibration import *
from graphWindow import *
from calibration import *
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from PySide6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph import PlotWidget

# Set up logging configuration.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def setup_graph_widgets(main_window):
    """
    Replace static placeholders in the UI with pyqtgraph PlotWidgets.
    """
    # Replace size placeholder
    size_layout = QVBoxLayout(main_window.ui.sizeGraphWidget)  # Target layout in the placeholder widget
    main_window.size_graph = PlotWidget()  # Create the PlotWidget for size graphs
    main_window.size_graph.setBackground('w')  # Set white background
    main_window.size_graph.setLabel("bottom", "Particle Size (px)")
    main_window.size_graph.setLabel("left", "Frequency")
    main_window.size_graph.showGrid(x=True, y=True)  # Enable grid
    size_layout.addWidget(main_window.size_graph)  # Attach PlotWidget dynamically to the layout

    # Replace velocity placeholder
    velocity_layout = QVBoxLayout(main_window.ui.velocityGraphWidget)  # Target layout in the placeholder widget
    main_window.velocity_graph = PlotWidget()  # Create the PlotWidget for velocity graphs
    main_window.velocity_graph.setBackground('w')  # Set white background
    main_window.velocity_graph.setLabel("bottom", "Velocity (px/frame)")
    main_window.velocity_graph.setLabel("left", "Frequency")
    main_window.velocity_graph.showGrid(x=True, y=True)  # Enable grid
    velocity_layout.addWidget(main_window.velocity_graph)  # Attach PlotWidget dynamically to the layout


########################################################################################
# MAIN WINDOW CLASS
########################################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Dynamically set up the graphs
        # setup_graph_widgets(self)

        # Camera initialization
        self.camera_dialog = VideoCalibrationDialog(self)
        self.graph_window = GraphWindow(self)
        self.calibration_dialog = None
        self.optical_metrology_module = OpticalMetrologyModule(debug=False, parent_ui=self.ui)

        # Initialize variables for size and velocity graph bins
        self.size_bins = np.linspace(0, 100, 21)  # Modify ranges according to expected sizes
        self.velocity_bins = np.linspace(0, 50, 21)  # Modify ranges according to expected velocities

        # Video capture and output settings
        #self.cam = cv2.VideoCapture('Test Data/Videos/3.mp4')  # Provide the path to your video
        #self.fps = int(self.cam.get(cv2.CAP_PROP_FPS))

        # Apply JSON stylesheet
        loadJsonStyle(self, self.ui)
        self.show()  # Show window

        parent_widget = self.ui.menuBtn.parent()
        if parent_widget:
            parent_widget.show()

        self.ui.menuBtn.raise_()

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

        # Connect other buttons
        self.ui.cameraBtn.clicked.connect(self.open_video_calibration_dialog)
        self.ui.graphBtn.clicked.connect(self.open_graph_window)

        self.saveDataCheckBox.stateChanged.connect(self.on_save_data_checkbox_changed)

    def open_video_calibration_dialog(self):
        # Show the dialog (modal, blocks interaction with the main window)
        self.camera_dialog.show()

    def open_graph_window(self):
        # Show the window
        self.graph_window.show()

    def on_save_data_checkbox_changed(self, state):
        if state == QtCore.Qt.Checked:
            logging.info("Save Data option enabled.")
        else:
            logging.info("Save Data option disabled.")

    # def get_current_frame(self):
    #     ret, frame = self.cam.read()
    #     if not ret:  # End of video or error
    #         self.cam.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video if needed
    #         logging.info("Restarting video playback.")
    #         ret, frame = self.cam.read()
    #     return frame if ret else None

########################################################################################
# GRAPH WINDOW CLASS
########################################################################################
class GraphWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("SizeandVelocityGraph.ui", self)
        # self.ui = Ui_GraphWindow()
        # self.ui.setupUi(self)

        self.size_graph = self.findChild(PlotWidget, "sizeGraphWidget")
        # self.size_graph.showGrid(x=True, y=True)
        #
        self.velocity_graph = self.findChild(PlotWidget, "velocityGraphWidget")
        # self.velocity_graph.showGrid(x=True, y=True)
        # Initialize the plot widgets with correct parent
        # self.size_graph = pg.PlotWidget(parent=self.findChild(QtWidgets.QWidget, "sizeGraphWidget"))
        # self.velocity_graph = pg.PlotWidget(parent=self.findChild(QtWidgets.QWidget, "velocityGraphWidget"))

        # self.show()

        # Set up the plot widgets
        # self.setup_plots()

    def setup_plots(self):
        # Configure size graph
        self.size_graph.setBackground('w')
        self.size_graph.setLabel("bottom", "Particle Size (px)")
        self.size_graph.setLabel("left", "Frequency")
        self.size_graph.showGrid(x=True, y=True)

        # Configure velocity graph
        self.velocity_graph.setBackground('w')
        self.velocity_graph.setLabel("bottom", "Velocity (px/frame)")
        self.velocity_graph.setLabel("left", "Frequency")
        self.velocity_graph.showGrid(x=True, y=True)


    def update_graphs(self):
        # Update size graph
        self.size_graph.clear()
        self.size_graph.plot(self.size_data, pen='b', symbol='o')

        # Update velocity graph
        self.velocity_graph.clear()
        self.velocity_graph.plot(self.velocity_data, pen='r', symbol='x')

########################################################################################
# CALIBRATION DIALOG CLASS
########################################################################################
class CalibrationDialog(QDialog):
    def __init__(self, distance, parent=None):
        super().__init__(parent)
        self.ui = Ui_CalibrationDialog()
        self.ui.setupUi(self)
        self.parent = parent

        self.pixelDistance = distance
        self.pixels_mm_ratio = None

        # Set the config path relative to the script location
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.json')

        # Connect a button to perform the pixel/mm ratio calculation
        self.ui.okBtn.clicked.connect(self.calculate_pixel_mm_ratio)

        # Display the distance in pixelDistanceTextEdit
        self.set_pixel_distance()

    def set_pixel_distance(self):
        """Set the calculated distance in the pixelDistanceTextEdit."""
        self.ui.pixelDistanceTextEdit.setPlainText(str(self.pixelDistance))

    def calculate_pixel_mm_ratio(self):
        """Calculate and display the pixel/mm ratio."""
        try:
            # Get the distance in pixels and known distance
            pixel_distance = float(self.ui.pixelDistanceTextEdit.toPlainText().strip())
            known_distance = float(self.ui.knownDistanceTextEdit.toPlainText().strip())

            # Check if known_distance is not zero to avoid division by zero
            if known_distance == 0:
                self.ui.resultTextEdit.setPlainText("Error: Known distance cannot be zero.")
                return

            # Calculate the pixel/mm ratio
            self.pixels_mm_ratio = pixel_distance / known_distance

            # Display the result in the resultLabel or another designated widget
            self.ui.resultTextEdit.setPlainText(f"{self.pixels_mm_ratio:.4f}")

            self.save_config()

            # Notify the user that calibration is complete
            self.show_calibration_complete_message()

        except ValueError:
            # Handle invalid input errors
            self.ui.resultTextEdit.setPlainText("Error: Please enter valid numbers in both fields.")

    def save_config(self):
        """Save the current pixel/mm ratio to `config.json`."""

        try:
            config = {}
            # If the file exists, load existing content to preserve it
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    config = json.load(f)

            # Update the scaling factor
            config["scaling_factor"] = {"pixels_per_mm": self.pixels_mm_ratio}

            # Save back to config.json
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=4)
            if self.debug:
                print("Config updated with new pixel/mm ratio.")

        except Exception as e:
            print(f"Error saving config: {e}")

    def show_calibration_complete_message(self):
        """Display an alert about the completion of calibration."""
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle("Calibration Complete")
        message_box.setText("The calibration has been completed successfully!")
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec_()

    def closeEvent(self, event):
        """Ensure closing the dialog doesn't close the application. Return to main window."""
        self.hide()  # Hide the dialog instead of closing it
        if self.parent:
            self.parent.show()  # Show the main window again
        event.ignore()  # Stop the default close behavior

########################################################################################
# VIDEO CALIBRATION DIALOG CLASS
########################################################################################
class VideoCalibrationDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_VideoCalibrationDialog()
        self.ui.setupUi(self)
        self.calibration_dialog = None
        self.parent = parent

        self.video_processor = None  # VideoProcessor instance
        self.camera_connected = False  # Flag to track camera connection

        # Attempt to check camera connectivity
        self.camera_connected = self.check_camera_connection()

        # If a camera is connected, initialize live video feed
        if self.camera_connected:
            self.video_processor = VideoProcessor(self.ui.videoLabel)
            self.start_video_feed()
        else:
            self.display_no_camera_message()

        # Timer for periodic video feed updates
        self.timer = QTimer(self)

        self.imported_image_path = None  # Store the path of the imported image

        self.ui.videoLabel.setContentsMargins(0, 0, 0, 0)  # Remove content margins
        self.ui.videoLabel.setStyleSheet("padding: 0px; margin: 0px; border: none;")  # Ensure no padding or border

        # Connect buttons
        self.ui.screenshotBtn.clicked.connect(self.capture_screenshot)
        self.ui.lineMeasurementBtn.clicked.connect(self.start_measurement)
        self.ui.importPictureBtn.clicked.connect(self.import_picture)  # Connect import picture button

        self.current_frame = None
        self.screenshot_captured = False
        self.measurement_started = False
        self.start_point = None
        self.end_point = None
        self.screenshot_pixmap = None
        self.painter = None
        self.original_image = None
        self.x_scale = None
        self.y_scale = None
        self.x_offset = None
        self.y_offset = None
        self.distance = None

        # Enable mouse events on QLabel
        self.ui.videoLabel.setMouseTracking(True)

        self.ui.nextBtn.clicked.connect(self.open_calibration_dialog)

    def open_calibration_dialog(self):
        # Show the dialog (modal, blocks interaction with the main window)
        try:
            self.calibration_dialog = CalibrationDialog(self.distance, self)
            self.calibration_dialog.show()
            print("Calibration dialog successfully opened.")
        except Exception as e:
            print(f"Error opening calibration dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open calibration dialog: {e}")


    def check_camera_connection(self):
        """Check if a ThorLabs camera is connected."""
        try:
            with TLCameraSDK() as sdk:
                available_cameras = sdk.discover_available_cameras()
                if len(available_cameras) > 0:
                    print(f"Camera(s) detected: {available_cameras}")
                    return True  # Camera is connected
                else:
                    print("No cameras detected.")
                    return False  # No camera found
        except Exception as e:
            print(f"Error checking camera connection: {e}")
            return False  # Error indicates no connection

    # Function to handle the display of a message to inform the user that there was no camera detected.
    def display_no_camera_message(self):
        """Display a message on the videoLabel when no camera is connected."""
        self.ui.videoLabel.clear()  # Clear any existing pixmap or content
        self.ui.videoLabel.setText("No camera connected.\nPlease check your connection or import calibration image.")
        self.ui.videoLabel.setAlignment(Qt.AlignCenter)  # Center-align the text
        self.ui.videoLabel.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")

    # Function to handle the import of a microsphere calibration image.
    def import_picture(self):
        """Allow the user to select a picture from their local computer and display it."""
        # Open a file dialog for the user to select a file
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpeg *.jpg *.bmp *.tif *.tiff)")  # Allowed image formats
        file_dialog.setFileMode(QFileDialog.ExistingFile)  # Ensure only files can be selected

        if file_dialog.exec_():
            # Get the selected file path
            self.imported_image_path = file_dialog.selectedFiles()[0]

            # Load and display the selected image
            self.display_imported_image(self.imported_image_path)

    # Function to display the selected calibration image in the video label.
    def display_imported_image(self, image_path):
        """Display the imported image in the videoLabel."""
        # Load the image using OpenCV
        image = cv2.imread(image_path)
        if image is None:
            print("Failed to load the image!")
            return

        # Convert OpenCV BGR image to RGB for display
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.original_image = rgb_image  # Store the original image
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w

        # Convert to QImage and then to QPixmap
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(q_image)

        # Fetch videoLabel's dimensions
        label_width = self.ui.videoLabel.width()
        label_height = self.ui.videoLabel.height()

        # Scale the QPixmap to fit within the videoLabel while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Store scaling factors for click mapping
        self.x_scale = w / scaled_pixmap.width()  # Width scaling factor
        self.y_scale = h / scaled_pixmap.height()  # Height scaling factor

        # Calculate offsets, including safety adjustment
        self.x_offset = max((label_width - scaled_pixmap.width()) // 2, 0)
        self.y_offset = max((label_height - scaled_pixmap.height()) // 2, 0)

        print(f"Image Size: {w}x{h}, QLabel Size: {label_width}x{label_height}")
        print(f"Scale Factors: x_scale={self.x_scale}, y_scale={self.y_scale}")
        print(f"Offsets: x_offset={self.x_offset}, y_offset={self.y_offset}")

        # Set the scaled pixmap to the videoLabel
        self.ui.videoLabel.setPixmap(scaled_pixmap)

    def start_video_feed(self):
        self.timer = self.startTimer(6)  # Timer event updates every 6ms

    def stop_video_feed(self):
        """Stop the QTimer to pause video feed."""
        self.timer.stop()

    def update_video_feed(self):
        """Fetch the video frame from VideoProcessor and display it."""
        frame = self.video_processor.process_frame()
        if frame is not None:
            # Convert OpenCV frame to QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)

            # Display the pixmap on videoLabel
            self.ui.videoLabel.setPixmap(pixmap)

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

    # Function to start the line measurement tool.
    def start_measurement(self):
        """Start the measurement process when the button is clicked."""
        # Check if either a screenshot has been captured or an imported image is displayed
        if not self.screenshot_captured and not (self.imported_image_path and not self.ui.videoLabel.pixmap().isNull()):
            print("Please capture a screenshot or import an image before starting the measurement.")
            return

        # Draw the grid on the pixmap
        self.draw_grid()
        self.measurement_started = True
        self.start_point = None
        self.end_point = None
        print("Measurement started. Select two points on the image.")

        self.ui.videoLabel.mousePressEvent = self.select_point

    def select_point(self, event):
        """Handle mouse click events for point selection."""
        if not self.measurement_started:
            print("Measurement has not started. Please click the Measure button first.")
            return  # Do nothing if measurement has not been started

        # Ensure the QLabel has a pixmap and it's not null
        pixmap = self.ui.videoLabel.pixmap()
        if pixmap is None or pixmap.isNull():
            print("No image available to measure.")
            return

        # Fetch the scaling applied to the pixmap inside the QLabel
        label_width = self.ui.videoLabel.width()
        label_height = self.ui.videoLabel.height()
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()

        # Calculate the scaled width and height while maintaining aspect ratio
        scaled_pixmap_width = pixmap_width
        scaled_pixmap_height = pixmap_height
        if pixmap_width > label_width or pixmap_height > label_height:
            scaled_pixmap = pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            scaled_pixmap_width = scaled_pixmap.width()
            scaled_pixmap_height = scaled_pixmap.height()

        # Calculate where the scaled pixmap is being drawn inside the QLabel
        x_offset = (label_width - scaled_pixmap_width) / 2
        y_offset = (label_height - scaled_pixmap_height) / 2

        # Get the click's position in the QLabel
        click_x = event.pos().x()
        click_y = event.pos().y()

        # Ensure the click is within the bounds of the displayed pixmap
        if click_x < x_offset or click_x > (x_offset + scaled_pixmap_width) or click_y < y_offset or click_y > (y_offset + scaled_pixmap_height):
            print("Click was outside the displayed image.")
            return

        # Map the QLabel click position to the pixmap's coordinates
        img_x = (click_x - x_offset) * pixmap_width / scaled_pixmap_width
        img_y = (click_y - y_offset) * pixmap_height / scaled_pixmap_height

        # Copy existing pixmap so we don't overwrite the original
        updated_pixmap = pixmap.copy()

        # Start drawing on the updated pixmap
        painter = QPainter(updated_pixmap)
        pen = QPen(Qt.red, 2)  # Set pen color and thickness for drawing
        painter.setPen(pen)
        painter.setBrush(Qt.red) # Use red brush for circles

        # Circle radius for point indication
        point_radius = 3

        # Log the result for debugging
        print(f"Click Position: ({click_x}, {click_y}) => Image Coordinates: ({img_x}, {img_y})")

        # Handle the point selection logic (e.g., drawing points, lines, or storing coordinates)
        if self.start_point is None:
            # First point selection
            self.start_point = (img_x, img_y)
            print(f"Start Point: ({img_x:.2f}, {img_y:.2f})")
            painter.drawEllipse(QPointF(img_x, img_y), point_radius, point_radius)  # Draw circle at the first point

        elif self.end_point is None:
            # Second point selection
            self.end_point = (img_x, img_y)
            print(f"End Point: ({img_x:.2f}, {img_y:.2f})")
            painter.drawEllipse(QPointF(img_x, img_y), point_radius, point_radius)  # Draw circle at the second point

            # Draw a line between start and end points
            painter.drawLine(QPointF(self.start_point[0], self.start_point[1]),
                             QPointF(self.end_point[0], self.end_point[1]))

            # Calculate and display the distance
            self.distance = self.calculate_and_display_distance()
            # Adding the text near the midpoint of the line
            mid_x = (self.start_point[0] + self.end_point[0]) / 2
            mid_y = (self.start_point[1] + self.end_point[1]) / 2
            painter.setPen(QPen(Qt.white))
            painter.drawText(QPointF(mid_x + 10, mid_y - 10), f"{self.distance:.2f} px")

            # Reset start and end points for the next measurement
            self.start_point = None
            self.end_point = None
            print("Measurement complete.")

            # Finish painting
        painter.end()

        # Update the QLabel with the newly drawn pixmap
        self.ui.videoLabel.setPixmap(updated_pixmap)

    def draw_grid(self):
        """Draw a grid over the current image displayed in the videoLabel."""
        pixmap = self.ui.videoLabel.pixmap()

        if pixmap is None:
            print("No image available to draw the grid.")
            return

        # Create a painter to draw on the pixmap
        painter = QPainter(pixmap)
        pen = QPen(Qt.gray, 1, Qt.SolidLine)  # Configure grid line color and thickness
        painter.setPen(pen)

        # Define grid spacing
        grid_spacing = 50  # Adjust this value to make the grid finer or coarser

        # Get the dimensions of the pixmap
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()

        # Draw vertical grid lines
        for x in range(0, pixmap_width, grid_spacing):
            painter.drawLine(x, 0, x, pixmap_height)

        # Draw horizontal grid lines
        for y in range(0, pixmap_height, grid_spacing):
            painter.drawLine(0, y, pixmap_width, y)

        painter.end()

        # Update the videoLabel with the updated pixmap (with the grid)
        self.ui.videoLabel.setPixmap(pixmap)

    def calculate_and_display_distance(self):
        if self.start_point and self.end_point:
            # Distance in pixels using Euclidean distance formula
            dx = self.end_point[0] - self.start_point[0]
            dy = self.end_point[1] - self.start_point[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5

            print(f"Measured Distance: {distance:.2f} pixels")  # Log to console
            return distance
        return 0

    def closeEvent(self, event):
        """Handle dialog close to ensure resources are cleaned up."""
        try:
            # Stop the video feed resources if it's running
            if hasattr(self, "timer") and self.timer.isActive():
                self.timer.stop()  # Stop the video feed updates
            if hasattr(self, "video_processor") and self.video_processor is not None:
                self.video_processor.camera.release()  # Release the camera resources

            # Hide the dialog instead of closing it
            self.hide()

            # Show the main window (parent)
            if self.parent is not None:
                self.parent.show()  # Safely return to the main window

            # Ignore the default close event, so it does not terminate the application
            event.ignore()

        except Exception as e:
            print(f"Error while closing the VideoCalibrationDialog: {e}")
            event.accept()  # Fallback: Close dialog if cleanup fails

def main():
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
        video_processor = VideoProcessor(window.ui.videoFeedLabel, input_mode="file", video_source="Test Data/Videos/3.mp4")
        if not video_processor.initialize_tracking():
            sys.exit(1)

        window.show()

        # Process video frame by frame
        timer = QTimer()

        def update_video():
            # Process the next frame in VideoProcessor
            processed_frame = video_processor.process_frame()
            if processed_frame is None:
                timer.stop()  # Stop the timer if no frames are returned
                return

            # Convert OpenCV frame to PyQt QPixmap
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            h, w, ch = rgb_frame.shape  # Get dimensions
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)

            # Scale the QPixmap to fit QLabel dimensions
            label_width = window.ui.videoFeedLabel.width()
            label_height = window.ui.videoFeedLabel.height()
            scaled_pixmap = pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Update QLabel
            window.ui.videoFeedLabel.setPixmap(scaled_pixmap)

        # Connect the timer to update video feed every 16 ms (~60 FPS)
        timer.timeout.connect(update_video)
        timer.start(16)

        # Start the Qt application loop
        sys.exit(app.exec_())

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()





# class RealTimeVideoProcessor:
#     def __init__(self, ui_video_label):
#         self.ui_video_label = ui_video_label
#         self.cam = cv2.VideoCapture('Test Data/Videos/3.mp4')
#
#         # Get the video's actual FPS
#         self.fps = int(self.cam.get(cv2.CAP_PROP_FPS))
#         print(f"Video is running at {self.fps} FPS.")
#
#         self.mask = None
#         self.particle_colors = []
#         self.trajectories = []
#         self.old_gray = None
#         self.p0 = None
#         self.prev_frame_time = 0
#         self.new_frame_time = 0
#         # For FPS calculation
#         self.frame_count = 0
#         self.start_time = time.time()
#         self.prev_frame_time = 0
#         self.new_frame_time = 0
#         # Parameters for goodFeaturesToTrack and Lucas-Kanade Optical Flow
#         self.feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
#         self.lk_params = dict(winSize=(15, 15), maxLevel=2,
#                               criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
#
#     def initialize_tracking(self):
#         ret, old_frame = self.cam.read()
#         if not ret:
#             print("Error reading the video file.")
#             return False
#         self.old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
#         self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask=None, **self.feature_params)
#         if self.p0 is not None:
#             # Assign a unique color to each particle based on its index
#             self.particle_colors = {
#                 i: self.get_random_color() for i in range(len(self.p0))
#             }
#         self.mask = np.zeros_like(old_frame)
#         return True
#
#     @staticmethod
#     def get_random_color():
#         return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
#
#     def process_frame(self):
#         ret, frame = self.cam.read()
#         if not ret:
#             print("Video processing complete.")
#             return None
#
#         # Calculate FPS using moving average
#         self.frame_count += 1
#         elapsed_time = time.time() - self.start_time
#
#         if elapsed_time > 0:
#             current_fps = self.frame_count / elapsed_time
#             # Reset counters every second to maintain accuracy
#             if elapsed_time > 1:
#                 self.frame_count = 0
#                 self.start_time = time.time()
#         else:
#             current_fps = self.fps
#
#         # Draw FPS on the frame
#         cv2.putText(frame, f"FPS: {int(current_fps)}",
#                     (10, 80),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     3, (255, 255, 255), 2,
#                     cv2.LINE_AA)
#
#         frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#         # Calculate optical flow to get new positions of tracked points
#         p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.p0, None, **self.lk_params)
#         good_new = p1[st == 1] if p1 is not None else None
#         good_old = self.p0[st == 1] if self.p0 is not None else None
#
#         # If points are valid, update trajectories and draw uniform-colored lines
#         if good_new is not None and good_old is not None:
#             for i, (new, old) in enumerate(zip(good_new, good_old)):
#                 a, b = int(new[0]), int(new[1])
#                 c, d = int(old[0]), int(old[1])
#
#                 # Draw the trajectory line in a single fixed color (e.g., green)
#                 fixed_color = (0, 255, 0)  # Green color for all trajectories
#                 self.mask = cv2.line(self.mask, (a, b), (c, d), fixed_color, 2)
#
#                 # Append points to trajectories for further usage/analysis
#                 if i >= len(self.trajectories):
#                     self.trajectories.append([(a, b)])
#                 else:
#                     self.trajectories[i].append((a, b))
#                     # Trim trajectory length to at most 10 points
#                     if len(self.trajectories[i]) > 10:
#                         self.trajectories[i].pop(0)
#
#         # Combine the original frame with the updated trajectory mask
#         output = cv2.add(frame, self.mask)
#
#         # Update the state for the next frame
#         self.old_gray = frame_gray.copy()
#         self.p0 = good_new.reshape(-1, 1, 2) if good_new is not None else None
#
#         return output

    # def select_point(self, event):
    #     """Handle mouse click events for point selection."""
    #     if not self.measurement_started:
    #         print("Measurement has not started. Please press the Measure button first.")
    #         return  # Do nothing if measurement has not been started
    #
    #     # Ensure the QLabel has a pixmap and it's not null
    #     pixmap = self.ui.videoLabel.pixmap()
    #     if pixmap is None or pixmap.isNull():  # Ensure there is a pixmap to draw on
    #         print("No pixmap available to draw on.")
    #         return
    #
    #     # Get the position of the click in QLabel coordinates
    #     click_x = event.pos().x()
    #     click_y = event.pos().y()
    #
    #     # Adjust for QLabel padding offsets
    #     adjusted_x = click_x - self.x_offset
    #     adjusted_y = click_y - self.y_offset
    #
    #     # Ensure the click is within the displayed region
    #     if adjusted_x < 0 or adjusted_y < 0:
    #         print("Click outside the displayed image")
    #         return
    #     if adjusted_x > self.ui.videoLabel.pixmap().width() or adjusted_y > self.ui.videoLabel.pixmap().height():
    #         print("Click outside the displayed image")
    #         return
    #
    #     # Map QLabel click position to original image coordinates
    #     img_x = int(adjusted_x * self.x_scale)
    #     img_y = int(adjusted_y * self.y_scale)
    #
    #     # Debug the adjusted coordinates
    #     print(f"Click QLabel Position: ({click_x}, {click_y})")
    #     print(f"Adjusted Position: ({adjusted_x}, {adjusted_y}) -> Original Image: ({img_x}, {img_y})")
    #
    #     # Handle point selection
    #     pixmap = self.ui.videoLabel.pixmap().copy()
    #
    #     if pixmap:
    #
    #         # Create a painter object to draw on the image
    #         self.painter = QPainter(pixmap)
    #         pen = QPen(Qt.red, 2, Qt.SolidLine)
    #         self.painter.setPen(pen)
    #
    #         # Draw the circle for the selected point
    #         point_radius = 3
    #
    #         if self.start_point is None:
    #             # Store the first point
    #             self.start_point = QPoint(img_x, img_y)
    #             print(f"First Point Selected: ({img_x}, {img_y})")
    #             # Draw a circle at the first point
    #             self.painter.drawEllipse(event.pos(), point_radius, point_radius)
    #
    #         elif self.end_point is None:
    #             # Store the second point
    #             self.end_point = QPoint(img_x, img_y)
    #             print(f"Second Point Selected: ({img_x}, {img_y})")
    #             # Draw the circle at the second point
    #             self.painter.drawEllipse(event.pos(), point_radius, point_radius)
    #
    #             self.painter.drawLine(self.start_point, self.end_point)  # Draw a line connecting the two points
    #
    #             # Calculate distance and draw the result
    #             self.calculate_and_display_distance(self.painter)
    #
    #         self.painter.end()
    #
    #         # Update the videoLabel with the updated pixmap
    #         self.ui.videoLabel.setPixmap(pixmap)