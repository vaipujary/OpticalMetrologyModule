import numpy as np
import random
import time
import cv2
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK

class VideoProcessor:
    def __init__(self, ui_video_label, input_mode="file", video_source=None):
        self.ui_video_label = ui_video_label
        self.input_mode = input_mode
        self.video_source = video_source

        self.camera = None

        if input_mode == "live":
            try:
                from windows_setup import configure_path
                configure_path()
                self._setup_camera()
            except ImportError:
                configure_path = None
        elif input_mode == "file" and video_source is not None:
            self.camera = cv2.VideoCapture(video_source)
        else:
            raise ValueError("Invalid input_mode.Use 'file' or 'live', and provide a valid video_source for file input.")


        self.mask = None
        self.fps = None
        self.frame_count = 0
        self.start_time = time.time()
        self.particle_colors = []
        self.trajectories = {}
        self.id_mapping = {}
        self.old_gray = None
        self.p0 = None
        self.prev_frame_time = 0
        self.new_frame_time = 0

        # Parameters for goodFeaturesToTrack and Lucas-Kanade Optical Flow
        self.feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    def __del__(self):
        """Destructor to clean up resources when the object is garbage collected."""
        self._cleanup_resources()

    def _setup_camera(self):
        """Initialize ThorCam camera."""
        # Properly close the camera if it was opened
        if hasattr(self, "camera") and self.camera:
            try:
                self.sdk = TLCameraSDK()
                available_cameras = self.sdk.discover_available_cameras()
                if len(available_cameras) < 1:
                    raise Exception("No cameras detected.")

                #with self.sdk.open_camera(available_cameras[0]) as camera:
                self.camera = self.sdk.open_camera(available_cameras[0])
                self.camera.exposure_time_us = 10000  # Set exposure to 10 ms
                self.camera.frames_per_trigger_zero_for_unlimited = 0
                self.camera.image_poll_timeout_ms = 1000  # 1 second polling timeout
                self.camera.frame_rate_control_value = 10
                self.camera.is_frame_rate_control_enabled = True

                self.camera.arm(2)
                self.camera.issue_software_trigger()
            except Exception as e:
                print(f"Error initializing camera: {e}")
                self._cleanup_resources()
                raise

    def _cleanup_resources(self):
        """Ensure all resources are cleaned up properly."""
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


    def initialize_tracking(self):
        """Initialize the particle tracking by capturing the initial frame."""
        frame = self._get_frame()
        if frame is None:
            print("Error: Unable to retrieve the initial frame.")
            return False

        # Convert to grayscale
        self.old_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect initial particle features
        self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask=None, **self.feature_params)
        if self.p0 is not None:
            # Assign random colors to features
            # self.particle_colors = {i: self.get_random_color() for i in range(len(self.p0))}
            self.particle_colors = [self.get_random_color() for _ in range(len(self.p0))]
        # Initialize the mask for drawing trajectories
        self.mask = np.zeros_like(frame)
        return True

    def _get_frame(self):
        """Retrieve a frame from the ThorCam camera, process it into RGB format."""

        if self.input_mode == "live":
            if self.camera is not None:
                frame = self.camera.get_pending_frame_or_null()
                if frame is not None:
                    frame.image_buffer
                    # Reshape and convert the grayscale frame into an RGB format
                    image_buffer = np.copy(frame.image_buffer)
                    # reshaped_frame = image_buffer.reshape(self.camera.image_height_pixels, self.camera.image_width_pixels)

                    numpy_shaped_image = image_buffer.reshape(self.camera.image_height_pixels,
                                                                   self.camera.image_width_pixels)
                    nd_image_array = np.full((self.camera.image_height_pixels, self.camera.image_width_pixels, 3), 0,
                                             dtype=np.uint8)
                    nd_image_array[:, :, 0] = numpy_shaped_image
                    nd_image_array[:, :, 1] = numpy_shaped_image
                    nd_image_array[:, :, 2] = numpy_shaped_image

                    return nd_image_array
        elif self.input_mode == "file":
            ret, frame = self.camera.read()
            return frame if ret else None
        return None

    @staticmethod
    def get_random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def process_frame(self):
        """Process frame, update particle trajectories, and draw on mask."""

        frame = self._get_frame()
        if frame is None:
            print("Error: Could not grab frame.")
            return None

        self.frame_count += 1
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Reset the mask for the current frame
        self.mask = np.zeros_like(frame)

        # 1. Manage Lost Particles and Update Trajectories
        new_p0 = []
        new_id_mapping = {}

        if self.p0 is not None:
            p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.p0, None, **self.lk_params)

            if p1 is not None:
                for i, (new, old) in enumerate(zip(p1, self.p0)):
                    a, b = new.ravel()
                    c, d = old.ravel()
                    particle_id = self.id_mapping.get(tuple(old.ravel()))  # Use existing ID

                    if particle_id is not None and st[i, 0] == 1:  # Check tracking status
                        new_id_mapping[(a, b)] = particle_id  # Update position in ID mapping
                        new_p0.append(new)  # Keep for next frame

                        # Draw trajectory (last 10 points)
                        if particle_id in self.trajectories:
                            self.trajectories[particle_id].append((a, b))
                        else:
                            self.trajectories[particle_id] = [(a, b)]  # Initialize if new

                        self.trajectories[particle_id] = self.trajectories[particle_id][-30:]
                        for k in range(1, len(self.trajectories[particle_id])):
                            pt1 = self.trajectories[particle_id][k - 1]
                            pt2 = self.trajectories[particle_id][k]
                            cv2.line(self.mask, (int(pt1[0]), int(pt1[1])),
                                     (int(pt2[0]), int(pt2[1])),
                                     self.particle_colors[particle_id], 2)

            self.p0 = np.array(new_p0).reshape(-1, 1, 2) if new_p0 else None
            self.id_mapping = new_id_mapping  # Update the ID mapping

        # 2. Detect New Particles and Assign Unique IDs
        if self.frame_count % 10 == 0 or self.p0 is None:  # Detect new features periodically
            new_features = cv2.goodFeaturesToTrack(frame_gray, mask=None, **self.feature_params)
            if new_features is not None:
                for new in new_features:
                    a, b = new.ravel()

                    if (a, b) not in self.id_mapping:  # Don't create a duplicate particle
                        particle_id = len(self.particle_colors)  # increment ID
                        self.particle_colors.append(self.get_random_color())
                        self.trajectories[particle_id] = [(a, b)]
                        self.id_mapping[(a, b)] = particle_id  # Create new particle
                        if self.p0 is not None:
                            self.p0 = np.vstack((self.p0, new.reshape(-1, 1, 2)))
                        else:
                            self.p0 = new.reshape(-1, 1, 2)

        output = cv2.add(frame, self.mask)
        self.old_gray = frame_gray.copy()
        return output