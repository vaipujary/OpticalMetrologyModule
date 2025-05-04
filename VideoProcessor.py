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
        self.CLAHE_CLIP = 2.0  # contrast-enhancement strength
        self.CLAHE_TILE = (8, 8)  # tile size for CLAHE
        self.BLUR_KSIZE = (5, 5)  # Gaussian blur kernel
        self.OTSU_OFFSET = -32  # “tighten” threshold: +N → stricter (smaller blobs)
        self.MIN_AREA_PX = 5  # noise reject  (same as before)

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
        self._last_size: dict[int, float] = {}  # <‑‑ remember last good size
        self.old_gray = None
        self.p0 = None

        # Parameters for goodFeaturesToTrack and Lucas-Kanade Optical Flow
        self.feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        # -------------- real‑time graph helpers -----------------
        self._particle_cache: dict[int, dict] = {}  # will hold last size/vel per id
        self._last_emit = 0.0  # time of last signal emission
        self._emit_interval = 0.05

        # ----------  REAL-TIME TRACKING STATE  ---------------------
        self.mask = None
        self.old_gray = None  # previous gray frame
        self.p0 = None  # points being tracked
        self.frame_count = 0
        self.tracking_started = False  # becomes True in initialize_tracking

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

        self.provisional = []  # list[(np.ndarray)]  new corners waiting for validation
        self.provisional_age = []  # parallel list – how many frames we tried
        self.provisional_traj = []  # 1‑to‑1 with provisional points
        self.coord_to_prov = {}

        self.MAX_PROV_AGE = 8  # discard if still invalid after N frames
        # -----------------------------------------------------------

    def __del__(self):
        """Destructor to clean up resources when the object is garbage collected."""
        self._cleanup_resources()

    def _reset_tracking_state(self):
        self.next_particle_id = 0
        self.trajectories.clear()
        self.id_mapping.clear()
        self.lost_counts.clear()
        self._last_size.clear()
        self._particle_cache.clear()

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
            if self.tracking_started:  # every 10th frame ≈165/10=16Hz
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
            if area < self.MIN_AREA_PX or area > 1e6:
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
        Update self._particle_cache **only for tracks that have
        both a finite size and velocity**.  Anonymous provisionals
        are*never* added to the cache (hence never get an ID).
        """
        if not self.tracking_started:
            return

        # ---- fresh size measurements (1 lookup per contour) -------------
        meas = self._measure_particles(gray_img)
        by_centroid = {m["centroid"]: m for m in meas}

        def size_at(pt):
            if not by_centroid:
                return None
            cx, cy = min(by_centroid,
                         key=lambda c: (c[0] - pt[0]) ** 2 + (c[1] - pt[1]) ** 2)
            return by_centroid[(cx, cy)]["area_diameter_um"]

        # ---- try to *promote* provisionals ------------------------------
        j = 0
        while j < len(self.provisional):
            traj = self.provisional_traj[j]
            traj.append(traj[-1])  # keep deque size
            if len(traj) < 2:  # need 2 pts for velocity
                j += 1
                continue

            # (1) give the point an ID right away (size/vel might be None)
            pid = self.next_particle_id
            self.next_particle_id += 1
            self.trajectories[pid] = traj
            self._last_size[pid] = None  # unknown for the moment
            self.lost_counts[pid] = 0

            self.id_mapping[self._q(traj[-1])] = pid

            # (2) move it out of the provisional lists
            self.provisional.pop(j)
            self.provisional_traj.pop(j)
            self.provisional_age.pop(j)
            continue
        # else:
        #     j += 1

        # ---- drop very old anonymous tracks -----------------------------
        for k in reversed(range(len(self.provisional_age))):
            if self.provisional_age[k] > self.MAX_PROV_AGE:
                self.provisional.pop(k)
                self.provisional_traj.pop(k)
                self.provisional_age.pop(k)

        # ---- build / refresh visible cache ------------------------------
        new_cache = {}
        for pid, traj in self.trajectories.items():
            if len(traj) < 2:
                continue
            size_um = size_at(traj[-1]) or self._last_size.get(pid)
            vel_mm = (self.calculate_velocity(traj, self.fps)
                      * self.scaling_factor / 1_000.0)

            # remember last good size
            if size_um is not None and np.isfinite(size_um):
                self._last_size[pid] = size_um

            # ---- NORMALISE for the GUI ----------------------------------
            # use 0when metric missing so graphs never leave a gap
            size_for_gui = size_um if (size_um is not None
                                       and np.isfinite(size_um)) else 0.0
            vel_for_gui = vel_mm if np.isfinite(vel_mm) else 0.0

            new_cache[pid] = {"size": float(size_for_gui),
                              "velocity": float(vel_for_gui)}
        # ---- keep the coord→index map in sync -----------------------------
        self.coord_to_prov = {self._q(pt): i
                              for i, pt in enumerate(self.provisional)}
        self._particle_cache.update(new_cache)

        # keep only the most recent 100 IDs
        if len(self._particle_cache) > 60:
            for old in sorted(self._particle_cache)[:-60]:
                self._particle_cache.pop(old, None)

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
        # print("FPS!!!:", self.camera.get_measured_frame_rate_fps())
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

    # VideoProcessor.py  (put it just after the imports inside the class)
    def _qimage_to_bgr(self, qimg: QImage) -> np.ndarray:
        """QImage  →  NumPy array in BGR order (for OpenCV)."""
        qimg = qimg.convertToFormat(QImage.Format_RGB888)
        w, h = qimg.width(), qimg.height()

        ptr = qimg.bits()
        ptr.setsize(h * w * 3)  # 3 channels
        arr = np.frombuffer(ptr, np.uint8).reshape((h, w, 3))

        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    @staticmethod
    def _q(pt: tuple[float, float]) -> tuple[int, int]:
        """Quantise a sub‑pixel corner to the nearest integer pixel centre.
        Used as a *stable* dictionary key from one frame to the next."""
        return (int(round(pt[0])), int(round(pt[1])))

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
        self._reset_tracking_state()
        self.tracking_started = False

        frame_obj = self.get_frame()
        if frame_obj is None:
            print("Error: couldn’t read first frame.")
            return False

        if isinstance(frame_obj, QImage):
            frame = self._qimage_to_bgr(frame_obj)
        else:
            frame = frame_obj

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
                self.id_mapping[self._q((x, y))] = pid
                self.lost_counts[pid] = 0

        self.tracking_started = True
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
        frame_obj = self.get_frame()
        if frame_obj is None:
            return None

        frame = (self._qimage_to_bgr(frame_obj)
                 if isinstance(frame_obj, QImage) else frame_obj)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # -------------------------------------------------- 1. LK update
        if self.p0 is not None:
            p1, st, _ = cv2.calcOpticalFlowPyrLK(
                self.old_gray, gray, self.p0, None, **self.lk_params)

            new_p0, new_map = [], {}
            seen_pids = set()

            if p1 is not None:
                for new, old, ok in zip(p1, self.p0, st):
                    if ok[0] != 1:
                        continue
                    a, b = new.ravel();
                    c, d = old.ravel()

                    # ------ existing ID track
                    pid = self.id_mapping.get(self._q((c, d)))
                    if pid is not None:
                        self.trajectories[pid].append((a, b))
                        new_map[self._q((a, b))] = pid
                        self.lost_counts[pid] = 0
                        seen_pids.add(pid)

                    # ------ anonymous track
                    else:
                        idx = self.coord_to_prov.pop(self._q((c, d)), None)
                        if idx is not None and idx < len(self.provisional):
                            self.provisional[idx] = (a, b)
                            self.provisional_traj[idx].append((a, b))
                            self.coord_to_prov[self._q((a, b))] = idx

                    new_p0.append(new)

            self.p0, self.id_mapping = (
                np.array(new_p0).reshape(-1, 1, 2) if new_p0 else None,
                new_map)

        # -------------------------------------------------- 2. new corners
        if self.frame_count % 10 == 0 or self.p0 is None:
            feats = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            if feats is not None:
                for f in feats:
                    x, y = f.ravel()
                    key = self._q((x, y))
                    if key in self.id_mapping or key in self.coord_to_prov:
                        continue
                    # store
                    self.provisional.append((x, y))
                    self.provisional_traj.append(deque([(x, y)],
                                                       maxlen=self.trajectory_length))
                    self.provisional_age.append(0)
                    self.coord_to_prov[key] = len(self.provisional) - 1   # store
                    # tell LK to track it
                    self.p0 = (f.reshape(1, 1, 2) if self.p0 is None
                               else np.vstack((self.p0, f.reshape(1, 1, 2))))

        # -------------------------------------------------- 3. lost IDs
        for pid in list(self.trajectories):
            if pid in seen_pids:
                continue
            self.lost_counts[pid] = self.lost_counts.get(pid, 0) + 1
            if self.lost_counts[pid] > self.lost_threshold:
                self.trajectories.pop(pid, None)
                self.lost_counts.pop(pid, None)

        # -------------------------------------------------- 4. cache & GUI
        self._update_particle_cache(gray)
        if (time.time() - self._last_emit > self._emit_interval
                and self._particle_cache):
            self.particles_metrics.emit(self._particle_cache.copy())
            self._last_emit = time.time()

        # -------------------------------------------------- 5. draw
        if self.mask is None:
            self.mask = np.zeros_like(frame)
        self.mask[:] = 0

        # real IDs – green
        for pid, tr in self.trajectories.items():
            for p, q in zip(tr, list(tr)[1:]):
                cv2.line(self.mask, (int(p[0]), int(p[1])),
                         (int(q[0]), int(q[1])), (0, 255, 0), 1)

        self.old_gray = gray.copy()
        self.frame_count += 1
        return cv2.add(frame, self.mask)