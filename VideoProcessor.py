import datetime
import threading
from collections import deque

import numpy as np
import time
import json
import cv2
import os, sys

from PyQt5.QtGui import QImage

from tsi_singleton import get_sdk

# absolute path to the folder that contains thorlabs_tsi_camera_sdk.dll
SDK_BIN = r"C:\Users\vaipu\PycharmProjects\OpticalMetrologyModule\dlls\64_lib"

if SDK_BIN not in os.environ["PATH"]:
    os.environ["PATH"] = SDK_BIN + os.pathsep + os.environ["PATH"]

# on Python 3.8+ add_dll_directory is the preferred way:
if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(SDK_BIN)
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from OpticalMetrologyModule import OpticalMetrologyModule

def load_pixels_per_mm(config_path="config.json"):
    """
    Load the pixels_per_mm value from the config.json file.

    :param config_path: Path to the configuration file.
    :return: pixels_per_mm value (float) or None if not found.
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        scaling_factor = float(config["scaling_factor"]["pixels_per_mm"])  # Access nested value
        return scaling_factor
    except (FileNotFoundError, KeyError, json.JSONDecodeError, TypeError) as e:
        print("Error loading pixels_per_mm from config.json:", e)
        return 1.0

class VideoProcessor:
    def __init__(self, ui_video_label, input_mode="file", video_source=None, save_data_enabled=False, particle_colors=None):

        self.save_data_enabled = save_data_enabled

        # Create a temporary CSV file for testing
        if self.save_data_enabled:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_csv = f"test_particle_data_{timestamp}.csv"
            self.optical_metrology_module = OpticalMetrologyModule(debug=False, output_csv=output_csv)
        else:
            self.optical_metrology_module = OpticalMetrologyModule(debug=False)

        self.ui_video_label = ui_video_label
        self.input_mode = input_mode
        self.video_source = video_source

        self.camera = None
        self.fps = None

        if input_mode == "live":
            try:
                from windows_setup import configure_path
                configure_path()
                self._setup_camera()  # store the Camera
                self.fps = float(getattr(self.camera,
                                         "actual_frame_rate", 165))  # fps
                self.mask = None
                self.latest_frame = None
                self.running = True
                self._grabber = threading.Thread(
                    target=self._acquisition_loop, daemon=True)
                self._grabber.start()
            except ImportError:
                configure_path = None
        elif input_mode == "file" and video_source is not None:
            self.camera = cv2.VideoCapture(video_source)
            self.fps = self.camera.get(cv2.CAP_PROP_FPS) or 30
            ret, frame = self.camera.read()
            if ret:
                self.mask = np.zeros_like(frame)

        else:
            raise ValueError("Invalid input_mode.Use 'file' or 'live', and provide a valid video_source for file input.")

        self.scaling_factor = load_pixels_per_mm()
        self.frame_count = 0
        self.start_time = time.time()
        self.particle_colors = particle_colors if particle_colors is not None else {}
        self.trajectories = {}
        self.id_mapping = {}

        self.particle_sizes = {}  # Dictionary to store sizes
        self.old_gray = None
        self.p0 = None

        # Parameters for goodFeaturesToTrack and Lucas-Kanade Optical Flow
        self.feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        # ----------  REAL-TIME TRACKING STATE  ---------------------
        self.mask = None
        self.old_gray = None  # previous gray frame
        self.p0 = None  # points being tracked
        self.frame_count = 0

        self.trajectories = {}  # pid → deque[(x,y)]
        self.id_mapping = {}  # (x,y) → pid
        self.next_particle_id = 0
        self.lost_counts = {}  # pid → # consecutive lost frames
        self.lost_threshold = 15
        self.trajectory_length = 30

        self.lk_params = dict(winSize=(20, 20),
                              maxLevel=4,
                              criteria=(cv2.TERM_CRITERIA_EPS |
                                        cv2.TERM_CRITERIA_COUNT, 30, 0.03))

        self.feature_params = dict(maxCorners=50,
                                   qualityLevel=0.4,
                                   minDistance=300,
                                   blockSize=7)
        # -----------------------------------------------------------

    def __del__(self):
        """Destructor to clean up resources when the object is garbage collected."""
        self._cleanup_resources()

    def _acquisition_loop(self):
        h, w = self.camera.image_height_pixels, self.camera.image_width_pixels
        self.camera.issue_software_trigger()  # queue first exposure
        while self.running:
            frame = self.camera.get_pending_frame_or_null()
            if frame is None:  # no frame ready yet
                time.sleep(0.0005)  # yield 0.5ms
                continue

            mono16 = np.frombuffer(frame.image_buffer, np.uint16,
                                   h * w).reshape(h, w)
            mono8 = (mono16 >> max(self.camera.bit_depth - 8, 0)).astype(np.uint8)

            qimg = QImage(mono8.data, w, h, w, QImage.Format_Grayscale8)
            qimg.ndarray_ref = mono8  # keep backing store alive
            # qimg = qimg.copy()
            self.latest_frame = qimg  # ← GUI will show this

            self.camera.issue_software_trigger()  # queue next one

    def _setup_camera(self):
        """
        Open the first available ThorLabs camera.
        Returns the camera object (not the fps).
        Raises RuntimeError if none can be opened.
        """
        self.sdk = get_sdk()
        serials = self.sdk.discover_available_cameras()
        if not serials:
            raise RuntimeError("No ThorLabs cameras detected.")

        self.camera = self.sdk.open_camera(serials[0])
        print("FPS!!!:", self.camera.get_measured_frame_rate_fps())
        if self.camera is None:
            raise RuntimeError("open_camera() returned None – is the camera in use?")

        # basic configuration…
        self.camera.exposure_time_us = 6000
        self.camera.frame_rate_control_value = 165
        self.camera.is_frame_rate_control_enabled = True
        self.camera.frames_per_trigger_zero_for_unlimited = 0
        self.camera.image_poll_timeout_ms = 10
        self.camera.operation_mode = 0

        self.camera.arm(2)
        self.camera.issue_software_trigger()


    def _cleanup_resources(self):
        """Ensure all resources are cleaned up properly."""
        print("Cleaning up resources...")
        # Properly close the camera if it was opened
        if hasattr(self, "camera") and self.camera:
            if self.input_mode == "live":  # Check input mode
                try:
                    print("Closing camera...")
                    self.camera.disarm()  # Disarm the camera
                    self.camera.close()  # Close the camera
                except Exception as e:
                    print(f"Error closing camera: {e}")
                self.camera = None
            elif self.input_mode == "file":  # For OpenCV VideoCapture
                self.camera.release()  # Properly release the VideoCapture resources

        # Properly dispose of the SDK if it was initialized
        if hasattr(self, "sdk") and self.sdk:
            try:
                print("Disposing SDK...")
                self.sdk.dispose()
            except Exception as e:
                print(f"Error disposing SDK: {e}")
            self.sdk = None

    def get_frame(self):
        """Retrieve a frame from the ThorCam camera, process it into RGB format."""
        if self.input_mode == "live":
            return self.latest_frame
            # if self.camera is not None:
            #     # self.camera.issue_software_trigger()
            #     frame = self.camera.get_pending_frame_or_null()
            #     if frame is None:
            #         # queue the *next* exposure right away
            #         self.camera.issue_software_trigger()
            #         return None
            #
            #     else:
            #         frame.image_buffer
            #         image_buffer_copy = np.copy(frame.image_buffer)
            #         numpy_shaped_image = image_buffer_copy.reshape(self.camera.image_height_pixels,
            #                                                        self.camera.image_width_pixels)
            #         nd_image_array = np.full((self.camera.image_height_pixels, self.camera.image_width_pixels, 3), 0,
            #                                  dtype=np.uint8)
            #         nd_image_array[:, :, 0] = numpy_shaped_image
            #         nd_image_array[:, :, 1] = numpy_shaped_image
            #         nd_image_array[:, :, 2] = numpy_shaped_image
            #
            #         # self.camera.issue_software_trigger()
            #         return nd_image_array

        elif self.input_mode == "file":
            ret, frame = self.camera.read()
            return frame if ret else None
        return None

    def initialize_tracking(self) -> bool:
        """Grab first frame and seed feature points / data structures."""
        frame = self.get_frame()
        if frame is None:
            print("Error: couldn’t read first frame.")
            return False

        self.old_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.mask = np.zeros_like(frame)

        self.p0 = cv2.goodFeaturesToTrack(self.old_gray,
                                          mask=None, **self.feature_params)
        if self.p0 is not None:
            for pt in self.p0:
                x, y = pt.ravel()
                pid = self.next_particle_id
                self.next_particle_id += 1

                self.trajectories[pid] = deque(maxlen=self.trajectory_length)
                self.trajectories[pid].append((x, y))
                self.id_mapping[(x, y)] = pid
                self.lost_counts[pid] = 0
        return True


    def calculate_velocity(self, trajectory, fps):
        """Calculate velocity from trajectory and frame rate."""
        if len(trajectory) < 2:
            return 0  # Cannot calculate velocity with less than two points

        dx = trajectory[-1][0] - trajectory[-2][0]
        dy = trajectory[-1][1] - trajectory[-2][1]

        # Calculate distance in pixels; you'll need a scaling factor to convert to real-world units (e.g., mm) if necessary.
        distance_pixels = np.sqrt(dx ** 2 + dy ** 2)

        # Velocity in pixels per second
        velocity = distance_pixels * fps

        return velocity

    def process_frame(self):
        """Return frame with particle trajectory overlay (no size/velocity yet)."""
        frame = self.get_frame()
        if frame is None:
            return None  # end of stream / error

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.mask is None:  # first call safety
            self.mask = np.zeros_like(frame)

        self.mask.fill(0)

        seen_this_frame = set()
        # ---------- optical flow on existing points -----
        new_p0, new_id_map = [], {}
        if self.p0 is not None:
            p1, st, _ = cv2.calcOpticalFlowPyrLK(
                self.old_gray, gray, self.p0, None, **self.lk_params)

            if p1 is not None:
                for new, old, s in zip(p1, self.p0, st):
                    a, b = new.ravel();
                    c, d = old.ravel()
                    pid = self.id_mapping.get((c, d))

                    if pid is not None and s[0] == 1:
                        new_id_map[(a, b)] = pid
                        new_p0.append(new)
                        self.trajectories[pid].append((a, b))
                        seen_this_frame.add(pid)
                        self.lost_counts[pid] = 0

                        # draw trajectory
                        pts = list(self.trajectories[pid])
                        for k in range(1, len(pts)):
                            cv2.line(self.mask,
                                     (int(pts[k - 1][0]), int(pts[k - 1][1])),
                                     (int(pts[k][0]), int(pts[k][1])),
                                     (0, 255, 0), 1)

        self.p0 = np.array(new_p0).reshape(-1, 1, 2) if new_p0 else None
        self.id_mapping = new_id_map

        # ---------- C: re-detect new features every 10 frames -----------
        if self.frame_count % 10 == 0 or self.p0 is None:
            tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, np.ones((5, 5), np.uint8))
            _, bin_ = cv2.threshold(tophat, 100, 255, cv2.THRESH_BINARY)

            feats = cv2.goodFeaturesToTrack(bin_, mask=None, **self.feature_params)
            if feats is not None:
                for f in feats:
                    a, b = f.ravel()
                    if (a, b) in self.id_mapping:
                        continue  # skip duplicates
                    pid = self.next_particle_id
                    self.next_particle_id += 1

                    self.trajectories[pid] = deque(maxlen=self.trajectory_length)
                    self.trajectories[pid].append((a, b))
                    self.id_mapping[(a, b)] = pid
                    self.lost_counts[pid] = 0

                    self.p0 = f.reshape(1, 1, 2) if self.p0 is None else np.vstack((self.p0, f.reshape(1, 1, 2)))

        # ---------- D: cull particles lost for too long -----------------
        for pid in list(self.lost_counts):
            if self.lost_counts[pid] > 50:
                self.trajectories.pop(pid, None)
                self.lost_counts.pop(pid, None)
                self.id_mapping = {k: v for k, v in self.id_mapping.items() if v != pid}

        for pid in list(self.trajectories):  # iterate over existing IDs
            if pid in seen_this_frame:
                self.lost_counts[pid] = 0
            else:
                self.lost_counts[pid] = self.lost_counts.get(pid, 0) + 1
                if self.lost_counts[pid] > self.lost_threshold:
                    # remove everything associated with that particle
                    self.trajectories.pop(pid, None)
                    self.lost_counts.pop(pid, None)
                    # purge from id_mapping
                    self.id_mapping = {k: v for k, v in self.id_mapping.items()
                                       if v != pid}

        # ---------- E: overlay trajectories -----------------------------
        combined = cv2.add(frame, self.mask)
        self.old_gray = gray
        self.frame_count += 1
        return combined