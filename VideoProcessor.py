import datetime
import threading
from collections import deque

import numpy as np
import time
import json
import cv2
import os
import math

from PyQt5.QtGui import QImage
from PyQt5.QtCore import QObject, pyqtSignal
from tsi_singleton import get_sdk

# absolute path to the folder that contains thorlabs_tsi_camera_sdk.dll
SDK_BIN = r"C:\Users\vaipu\PycharmProjects\OpticalMetrologyModule\dlls\64_lib"

CLAHE_CLIP        = 2.0       # contrast-enhancement strength
CLAHE_TILE        = (8, 8)    # tile size for CLAHE
BLUR_KSIZE        = (5, 5)    # Gaussian blur kernel
OTSU_OFFSET       = -32       # “tighten” threshold: +N → stricter (smaller blobs)
MIN_AREA_PX       = 5         # noise reject  (same as before)

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

class VideoProcessor(QObject):
    # emit {pid: {'size': float, 'velocity': float}}

    particles_metrics = pyqtSignal(dict)
    def __init__(self, ui_video_label, input_mode="file", video_source=None, save_data_enabled=False, particle_colors=None):
        super().__init__()
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

        # -------------- real‑time graph helpers -----------------
        self._particle_cache: dict[int, dict] = {}  # will hold last size/vel per id
        self._last_emit = 0.0  # time of last signal emission
        self._emit_interval = 0.20

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
        frame_counter = 0

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
            self.latest_frame = qimg  # ← GUI will show this

            # ------------- (very) light‑weight measurement --------     ⬅︎ NEW CODE
            frame_counter += 1
            if frame_counter % 10 == 0:  # every 10th frame ≈165/10=16Hz
                self._update_particle_cache(mono8)  # see helper below

            # ---- emit to GUI not faster than every 200ms -------------
            now = time.time()
            if now - self._last_emit > self._emit_interval and self._particle_cache:
                self.particles_metrics.emit(self._particle_cache.copy())
                self._last_emit = now

            self.camera.issue_software_trigger()  # queue next one

    def _measure_particles(self, gray: np.ndarray) -> list:
        """Return list of dicts ({'centroid':(x,y), 'size_um': …, …})."""
        clahe = cv2.createCLAHE(clipLimit=self.CLAHE_CLIP,
                                tileGridSize=self.CLAHE_TILE)
        enhanced = clahe.apply(gray)
        blurred = cv2.GaussianBlur(enhanced, self.BLUR_KSIZE, 0)

        t_otsu, _ = cv2.threshold(blurred, 0, 255,
                                  cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        strict_t = max(0, t_otsu + self.OTSU_OFFSET)
        _, binary = cv2.threshold(blurred, strict_t, 255,
                                  cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(binary,
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)  # :contentReference[oaicite:0]{index=0}
        return self._measure_from_contours(contours)

    def _measure_from_contours(self, contours):
        measurements = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            print("Area: ", area, "pixels")
            if area < MIN_AREA_PX or area > 1e6:
                continue

            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # (1) Area-based diameter, assuming circle
            area_diameter_pixels = math.sqrt(4.0 * area / math.pi)
            area_diameter_um = area_diameter_pixels * self.scaling_factor

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
                major_axis_um = MA * self.scaling_factor
                minor_axis_um = ma * self.scaling_factor

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
                ellipse_diameter_um = avg_diam_pixels * self.scaling_factor

                # Store the ellipse parameters
                ellipse_info = ellipse
            print("Diameter in px: ", area_diameter_pixels)
            print("Diameter in um: ", area_diameter_um)
            print("Ellipse Diameter: ", area_diameter_um)
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
    # ------------------------------------------------------------------
    def _update_particle_cache(self, gray_img: np.ndarray) -> None:
        """
            Build self._particle_cache{pid: {'size':µm, 'velocity':mms‑1}}.
            Called every N‑th frame from live _acquisition_loop
            *and* from process_frame when playing a file.
            """
        # --- A)sizes ----------------------------------------------------
        measurements = self._measure_particles(gray_img)
        by_centroid = {m["centroid"]: m for m in measurements}

        # quick helper to grab the nearest contour to a track‑point
        def nearest_size(px: float, py: float):
            if not by_centroid:
                return None
            cx, cy = min(by_centroid,
                         key=lambda c: (c[0] - px) ** 2 + (c[1] - py) ** 2)
            return by_centroid[(cx, cy)]["area_diameter_um"]

        # --- B)velocities + cache --------------------------------------
        new_cache = {}
        for pid, traj in self.trajectories.items():
            if len(traj) < 2:
                continue
            size_um = nearest_size(*traj[-1])  # might be None
            vel_mm = self.calculate_velocity(traj, self.fps) * self.scaling_factor / 1000.0
            new_cache[pid] = {"size": size_um, "velocity": vel_mm}

        self._particle_cache = new_cache

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

        elif self.input_mode == "file":
            ret, frame_bgr = self.camera.read()
            if not ret:
                return None

            # --- convert BGR ndarray → QImage -------------
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            h, w, _ = rgb.shape
            qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
            qimg.ndarray_ref = rgb  # keep buffer alive
            return qimg
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

        if self.frame_count % 3 == 0:  # measure every 3rd frame
            self._update_particle_cache(gray)

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

        if time.time() - self._last_emit > self._emit_interval and self._particle_cache:
            self.particles_metrics.emit(self._particle_cache.copy())
            self._last_emit = time.time()

        return combined