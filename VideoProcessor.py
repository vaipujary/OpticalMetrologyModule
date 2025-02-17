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
        self.trajectories = []
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
            try:
                print("Closing camera...")
                self.camera.disarm()  # Disarm the camera
                self.camera.close()  # Close the camera
            except Exception as e:
                print(f"Error closing camera: {e}")
            self.camera = None

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
            self.particle_colors = {i: self.get_random_color() for i in range(len(self.p0))}

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
        """Process each frame to calculate particle trajectories."""
        frame = self._get_frame()
        if frame is None:
            print("Error: Unable to retrieve a frame.")
            return None

        self.frame_count += 1
        elapsed_time = time.time() - self.start_time

        if elapsed_time > 0:
            fps = self.frame_count / elapsed_time
        else:
            fps = 0  # Prevent division by zero

        # Step 4: Overlay FPS on the frame
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 2,
                    cv2.LINE_AA)

        # Convert current frame to grayscale
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow to find new positions of tracked points
        if self.p0 is not None:
            p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.p0, None, **self.lk_params)

            # Keep only good points
            good_new = p1[st == 1] if p1 is not None else None
            good_old = self.p0[st == 1] if self.p0 is not None else None

            # Update trajectories and draw them
            if good_new is not None and good_old is not None:
                for i, (new, old) in enumerate(zip(good_new, good_old)):
                    a, b = int(new[0]), int(new[1])
                    c, d = int(old[0]), int(old[1])

                    # Draw the individual trajectory on the mask
                    self.mask = cv2.line(self.mask, (a, b), (c, d), self.particle_colors.get(i, (0, 255, 0)), 2)

                    # Save trajectory points
                    if i >= len(self.trajectories):
                        self.trajectories.append([(a, b)])
                    else:
                        self.trajectories[i].append((a, b))

                        # Keep at most 10 points for each trajectory
                        if len(self.trajectories[i]) > 10:
                            self.trajectories[i].pop(0)

        # Combine the frame with the trajectory mask
        output = cv2.add(frame, self.mask)

        # Update previous frame and points
        self.old_gray = frame_gray.copy()
        self.p0 = good_new.reshape(-1, 1, 2) if good_new is not None else None

        return output


