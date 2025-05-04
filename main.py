import json, tempfile, shutil
import math
from collections import deque
from tsi_singleton import get_sdk
import cv2
import logging
import numpy as np
import os
# Force PyQt5 usage:
os.environ["PYQTGRAPH_QT_LIB"] = "PyQt5"
import sys
import random
import time
from OpticalMetrologyModule import OpticalMetrologyModule
from VideoProcessor import VideoProcessor
from PyQt5.QtWidgets import QMessageBox, QDialog, QApplication, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, QPointF
from Custom_Widgets.Widgets import *
from mainWindow import *
from videoCalibration import *
from calibration import *
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK

# Set up logging configuration.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

########################################################################################
################################ MAIN WINDOW CLASS #####################################
########################################################################################
class MainWindow(QMainWindow):
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

    def __init__(self):
        # QMainWindow.__init__(self)
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Camera initialization
        self.camera_dialog = VideoCalibrationDialog(self)
        self.calibration_dialog = None
        self.optical_metrology_module = OpticalMetrologyModule(debug=False, parent_ui=self.ui)

        # Initialize variables for size and velocity graph bins
        self.size_bins = np.linspace(0, 100, 21)  # Modify ranges according to expected sizes
        self.velocity_bins = np.linspace(0, 50, 21)  # Modify ranges according to expected velocities

        # Apply JSON stylesheet
        loadJsonStyle(self, self.ui)

        parent_widget = self.ui.menuBtn.parent()
        if parent_widget:
            parent_widget.show()

        self.ui.menuBtn.raise_()

        self.ui.videoFeedLabel.setStyleSheet(
            "background-color: black; color: white; font-size: 18px;")
        self.ui.videoFeedLabel.setText("Please select input type")

        self.video_processor: VideoProcessor | None = None
        self.preview_timer = QTimer(self)
        self.preview_timer.setTimerType(Qt.PreciseTimer)
        self.preview_timer.timeout.connect(self._show_preview_frame)

        self.experiment_timer = QTimer(self)  # will be used later
        self.experiment_timer.setTimerType(Qt.PreciseTimer)
        self.ui.startBtn.clicked.connect(self._start_experiment)

        # ---- settings-menu widgets (radio buttons + save) ------------
        self.ui.fileRadioBtn.toggled.connect(self._on_radio_changed)  # optional visual feedback
        self.ui.liveRadioBtn.toggled.connect(self._on_radio_changed)
        self.ui.saveInputTypeBtn.clicked.connect(self._save_input_type)

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

        self.ui.experimentTimeComboBox.addItems(["10 minutes", "20 minutes", "30 minutes"])

        cfg = self._read_config()  # restore both settings
        self.ui.saveDataCheckBox.setChecked(cfg.get("save_data_enabled", False))

        saved_minutes = cfg.get("experiment_time_minutes", 10)
        index = {10: 0, 20: 1, 30: 2}.get(saved_minutes, 0)
        self.ui.experimentTimeComboBox.setCurrentIndex(index)

        # connect the button last
        self.ui.saveSettingsBtn.clicked.connect(self._save_general_settings)

        # Keep track of how many points we’ve plotted so far
        self.ptr = 0

        # Store data in lists
        self.max_points = 50
        self.x_data_size = []
        self.y_data_size = []
        self.x_data_vel = []
        self.y_data_vel = []

        # (Optional) Configure the initial look of the plots
        self.ui.sizePlotGraphicsView.setLabel('left', 'Size (microns)')
        self.ui.sizePlotGraphicsView.setLabel('bottom', 'Particle ID')
        self.ui.velocityPlotGraphicsView.setLabel('left', 'Velocity (mm/s)')
        self.ui.velocityPlotGraphicsView.setLabel('bottom', 'Particle ID')

        # # Create a timer to update these plots periodically
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_graphs)
        # self.timer.start(500)  # update every 200 ms

        # Store the time when we started
        self.start_time = time.time()

        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.update_elapsed_time)
        self.timer2.start(1000)  # 1 second interval

    def _start_experiment(self):
        if not self.video_processor:
            QMessageBox.warning(self, "No video source",
                                "Load a video or connect the camera first.")
            return

        # Stop the raw preview
        self.preview_timer.stop()

        # Initialise LK + feature tracking, etc.
        ok = self.video_processor.initialize_tracking()
        if not ok:
            QMessageBox.critical(self, "Error",
                                 "Could not initialise particle tracking.")
            return

        # Every timeout now calls the overlay/measurement pipeline
        self.experiment_timer.timeout.disconnect() if self.experiment_timer.receivers(
            self.experiment_timer.timeout) else None
        self.experiment_timer.timeout.connect(self._show_experiment_frame)
        gui_fps = 60
        self.experiment_timer.setInterval(int(1000 / gui_fps))
        self.experiment_timer.start()
        # period_ms = int(1000 / 165.5)
        # self.experiment_timer.start(period_ms)  # or e.g. 30 ms

    def _show_experiment_frame(self):
        frame = self.video_processor.process_frame()  # with trajectories
        if frame is None:  # end of file, camera error…
            self.experiment_timer.stop()
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape
        qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        self.ui.videoFeedLabel.setPixmap(QPixmap.fromImage(qimg))
        # rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # h, w, _ = rgb.shape
        # qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        # pix = QPixmap.fromImage(qimg).scaled(
        #     self.ui.videoFeedLabel.size(),
        #     Qt.KeepAspectRatio,
        #     Qt.SmoothTransformation)
        # self.ui.videoFeedLabel.setPixmap(pix)

    def _save_general_settings(self):
        """Persist checkbox + experiment duration to config.json."""
        # --- gather values from the UI --------------------------
        save_data = self.ui.saveDataCheckBox.isChecked()

        text = self.ui.experimentTimeComboBox.currentText()  # "20 minutes"
        minutes = int(text.split()[0])  # 10 / 20 / 30

        # --- merge with the existing config --------------------
        cfg = self._read_config()
        cfg["save_data_enabled"] = save_data
        cfg["experiment_time_minutes"] = minutes

        self._write_config(cfg)

        QMessageBox.information(self, "Settings", "Settings saved!")

    def _on_radio_changed(self):
        # Optional: immediately highlight the label so the user sees which one is active
        if self.ui.fileRadioBtn.isChecked():
            self.ui.videoFeedLabel.setText("File input selected – click Save")
        elif self.ui.liveRadioBtn.isChecked():
            self.ui.videoFeedLabel.setText("Live input selected – click Save")

    def _save_input_type(self):
        # 1) Which radio button is on?
        if self.ui.fileRadioBtn.isChecked():
            input_mode = "file"
        elif self.ui.liveRadioBtn.isChecked():
            input_mode = "live"
        else:
            QMessageBox.warning(self, "Input type", "Please choose File or Live first.")
            return

        # 2) Load existing config (if any) ---------------------------------
        try:
            if os.path.exists(self.CONFIG_PATH):
                with open(self.CONFIG_PATH, "r") as f:
                    cfg = json.load(f)
            else:
                cfg = {}
        except (json.JSONDecodeError, OSError):
            # Start fresh if the file is corrupt / unreadable
            cfg = {}

        # 3) Update just the key you care about ---------------------------
        cfg["input_mode"] = input_mode  # add / overwrite this one field

        # 4) Write back atomically so we never lose the file ---------------
        tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(self.CONFIG_PATH))
        try:
            with os.fdopen(tmp_fd, "w") as tmp:
                json.dump(cfg, tmp, indent=4)
            shutil.move(tmp_path, self.CONFIG_PATH)
        finally:
            if os.path.exists(tmp_path):  # clean up on failure
                os.remove(tmp_path)

        # 5) Launch the preview immediately -------------------------------
        try:
            self._start_preview(input_mode)
        except Exception as e:
            QMessageBox.critical(self, "Cannot start preview", str(e))

    def _start_preview(self, input_mode):
        # Guard: clean up a previous processor if the user flips choices
        if self.video_processor is not None:
            self.video_processor._cleanup_resources()
            self.preview_timer.stop()
            self.video_processor = None

        cfg = self._read_config()
        save_data = cfg.get("save_data_enabled", False)

        if input_mode == "file":
            video_path, _ = QFileDialog.getOpenFileName(
                self, "Choose video file", "", "Videos (*.mp4 *.avi *.mov)")
            if not video_path:
                self.ui.videoFeedLabel.setText("No file chosen.")
                return
            self.video_processor = VideoProcessor(
                ui_video_label=self.ui.videoFeedLabel,
                input_mode="file",
                video_source=video_path,
                save_data_enabled=save_data)

        else:  # live

            self.video_processor = VideoProcessor(
                ui_video_label=self.ui.videoFeedLabel,
                input_mode="live",
                save_data_enabled=save_data)

        # Immediately begin the raw preview (no tracking yet)
        self.preview_timer.start(0)

    def _show_preview_frame(self):
        if not self.video_processor:
            return

        frame = self.video_processor.get_frame()
        if frame is None:
            print("frame is None")
            return
        print("frame is not None")
        # Paint the BGR frame into the QLabel
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape

        # make the label exactly the camera size ONCE
        if self.ui.videoFeedLabel.width() != w or self.ui.videoFeedLabel.height() != h:
            self.ui.videoFeedLabel.setFixedSize(w, h)

        qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        self.ui.videoFeedLabel.setPixmap(QPixmap.fromImage(qimg))

    def open_video_calibration_dialog(self):
        # Show the dialog (modal, blocks interaction with the main window)
        self.camera_dialog.show()

    def open_graph_window(self):
        # Show the window
        self.graph_window.show()

    def update_elapsed_time(self):
        """Called by QTimer every second to update the label."""
        elapsed_seconds = time.time() - self.start_time
        minutes, seconds = divmod(elapsed_seconds, 60)
        # Format as MM:SS
        self.ui.timeElapsedLabel.setText(f"{int(minutes):02}:{int(seconds):02}")

    def update_graphs(self):
        # Increment our frame/index counter
        self.ptr += 1

        # Create new random data points
        new_size = np.random.uniform(10, 50)
        new_vel = np.random.uniform(1, 20)

        # Append to our data arrays
        self.x_data_size.append(self.ptr)
        self.y_data_size.append(new_size)

        self.x_data_vel.append(self.ptr)
        self.y_data_vel.append(new_vel)

        # If we exceed max_points, discard the oldest
        if len(self.x_data_size) > self.max_points:
            self.x_data_size.pop(0)
            self.y_data_size.pop(0)
        if len(self.x_data_vel) > self.max_points:
            self.x_data_vel.pop(0)
            self.y_data_vel.pop(0)

        # Clear existing plots before drawing new data
        self.ui.sizePlotGraphicsView.clear()
        self.ui.velocityPlotGraphicsView.clear()

        # Plot as scatter plots (no pen, just symbols)
        self.ui.sizePlotGraphicsView.plot(
            self.x_data_size, self.y_data_size,
            pen=None,  # no connecting line
            symbol='o',  # circle markers
            symbolSize=8,  # marker size
            symbolBrush='red'  # fill color
        )

        self.ui.velocityPlotGraphicsView.plot(
            self.x_data_vel, self.y_data_vel,
            pen=None,
            symbol='o',
            symbolSize=8,
            symbolBrush='blue'
        )

        # Set the x-range to show the newest max_points values
        # e.g., [self.ptr - max_points, self.ptr], so the plot "scrolls"
        left_bound = max(0, self.ptr - self.max_points)
        right_bound = self.ptr
        self.ui.sizePlotGraphicsView.setXRange(left_bound, right_bound, padding=0)
        self.ui.velocityPlotGraphicsView.setXRange(left_bound, right_bound, padding=0)

    def on_save_data_checkbox_changed(self, state):
        enabled = (state == Qt.Checked)

        cfg = self._read_config()  # merge, don’t overwrite
        cfg["save_data_enabled"] = enabled
        self._write_config(cfg)

        logging.info("Save Data option %s.", "enabled" if enabled else "disabled")

    # ----------  helpers for reading / writing config --------------
    def _read_config(self) -> dict:
        """Return existing JSON config or empty dict if file missing/bad."""
        try:
            with open(self.CONFIG_PATH, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def _write_config(self, cfg: dict) -> None:
        """Atomically replace the config file with the supplied dict."""
        import tempfile, os, shutil
        tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(self.CONFIG_PATH))
        with os.fdopen(tmp_fd, "w") as tmp:
            json.dump(cfg, tmp, indent=4)
        shutil.move(tmp_path, self.CONFIG_PATH)
    # ---------------------------------------------------------------


########################################################################################
############################ CALIBRATION DIALOG CLASS ##################################
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
######################### VIDEO CALIBRATION DIALOG CLASS ###############################
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
            self.video_processor = VideoProcessor(self.ui.videoLabel, input_mode="live")
# --- dedicated GUI timer: ------------------------------------------
            self.update_timer = QTimer(self)
            self.update_timer.setTimerType(Qt.PreciseTimer)
            self.update_timer.timeout.connect(self.update_video_feed)
            self.update_timer.start(33)
            # self.video_processor = VideoProcessor(self.ui.videoLabel, input_mode="live")
            # self.start_video_feed()

        else:
            self.display_no_camera_message()

        # Timer for periodic video feed updates
        #self.timer = QTimer(self)

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
        self.scaled_pixmap = None
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
            sdk = get_sdk()
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
        self.ui.videoLabel.setText('<div style="color:red; font-weight:bold; font-size:16px; text-align:center;">'
    'No camera connected.<br>Please check your connection or import calibration image.'
    '</div>')
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
        self.scaled_pixmap = pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Store scaling factors for click mapping
        self.x_scale = w / self.scaled_pixmap.width()  # Width scaling factor
        self.y_scale = h / self.scaled_pixmap.height()  # Height scaling factor

        # Calculate offsets, including safety adjustment
        self.x_offset = (label_width - self.scaled_pixmap.width()) // 2
        self.y_offset = (label_height - self.scaled_pixmap.height()) // 2

        print(f"Image Size: {w}x{h}, QLabel Size: {label_width}x{label_height}")
        print(f"Scale Factors: x_scale={self.x_scale}, y_scale={self.y_scale}")
        print(f"Offsets: x_offset={self.x_offset}, y_offset={self.y_offset}")

        # Set the scaled pixmap to the videoLabel
        self.ui.videoLabel.setPixmap(self.scaled_pixmap)

    def update_video_feed(self):
        """Fetch the video frame from VideoProcessor and display it."""
        frame = self.video_processor.get_frame()

        if frame is None:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape

        if self.ui.videoLabel.width() != w or self.ui.videoLabel.height() != h:
            self.ui.videoLabel.setFixedSize(w, h)

        qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        self.ui.videoLabel.setPixmap(QPixmap.fromImage(qimg))

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
            self.update_timer.stop()
            # self.killTimer(self.timer)  # Stop updating the video feed
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
        if not self.measurement_started:
            return

        # ---------------- click inside QLabel ----------------
        click_x, click_y = event.pos().x(), event.pos().y()

        # click must fall on the displayed pixmap
        if not (self.x_offset <= click_x <= self.x_offset + self.scaled_pixmap.width() and
                self.y_offset <= click_y <= self.y_offset + self.scaled_pixmap.height()):
            print("Click was outside the displayed image.")
            return

        # --------------- original-image coordinates ---------------
        img_x = (click_x - self.x_offset) * self.x_scale
        img_y = (click_y - self.y_offset) * self.y_scale

        # --------------- displayed-pixmap coordinates -------------
        disp_x = click_x - self.x_offset  # or  img_x / self.x_scale
        disp_y = click_y - self.y_offset  # or  img_y / self.y_scale

        # ------- draw on a copy of the pixmap currently shown -----
        pixmap = self.ui.videoLabel.pixmap()
        updated = pixmap.copy()

        painter = QPainter(updated)
        painter.setPen(QPen(Qt.red, 2))
        painter.setBrush(Qt.red)

        r = 3  # point radius

        if self.start_point is None:
            # first point
            self.start_point = (img_x, img_y)  # for distance
            self.start_display_pt = (disp_x, disp_y)  # for drawing
            painter.drawEllipse(QPointF(*self.start_display_pt), r, r)

        elif self.end_point is None:
            # second point
            self.end_point = (img_x, img_y)
            end_display_pt = (disp_x, disp_y)

            painter.drawEllipse(QPointF(*end_display_pt), r, r)
            painter.drawLine(QPointF(*self.start_display_pt), QPointF(*end_display_pt))

            # ---------- distance ----------
            self.distance = self.calculate_and_display_distance()

            # put label near the middle of the displayed line
            mid_x = (self.start_display_pt[0] + end_display_pt[0]) / 2
            mid_y = (self.start_display_pt[1] + end_display_pt[1]) / 2
            painter.setPen(QPen(Qt.white))
            painter.drawText(QPointF(mid_x + 10, mid_y - 10), f"{self.distance:.2f} px")

            # reset for next measurement
            self.start_point = self.end_point = None

        painter.end()
        self.ui.videoLabel.setPixmap(updated)

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
            distance = math.hypot(dx, dy)

            print(f"Measured Distance: {distance:.2f} pixels")  # Log to console
            return distance
        return 0

    def closeEvent(self, event):
        """Handle dialog close to ensure resources are cleaned up."""
        try:
            # Stop the video feed resources if it's running
            # if hasattr(self, "timer") and self.timer.isActive():
            #     self.timer.stop()  # Stop the video feed updates
            if hasattr(self, "update_timer") and self.update_timer.isActive():
                self.update_timer.stop()
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

    window = MainWindow()       # <- owns VideoProcessor & all timers
    window.show()

    sys.exit(app.exec_())       # start the event-loop

if __name__ == "__main__":
    main()