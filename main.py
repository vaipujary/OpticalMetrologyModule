import cv2
import time
import logging
import random
from OpticalMetrologyModule import OpticalMetrologyModule

# Set up logging configuration.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    # Capture video from the default camera (camera index 0).
    # cap = cv2.VideoCapture(0)
    cam = cv2.VideoCapture('/Sample Videos/3.mp4')
    frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cam.set(cv2.CAP_PROP_FPS, 30)  # Set the frame rate
    fourcc = cv2.VideoWriter.fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

    optical_metrology_module = OpticalMetrologyModule()

    # Get the experiment duration from the user (minimum 10 minutes), setting it to 10 mins for now.
    experiment_duration = 10
    start_time = time.time()

    # Assign random colors to each microsphere for trajectory visualization.
    colors = {}  # Dictionary to store colors for each microsphere ID

    # Begin the experiment.
    while True:
        # Check if the experiment duration has been reached.
        elapsed_time = time.time() - start_time
        if elapsed_time >= experiment_duration:
            logging.info("Experiment time completed.")  # End the experiment
            break

        # Read a frame from the video capture
        ret, frame = cam.read()
        if not ret:
            logging.error("Failed to capture image.")
            break

        out.write(frame)  # Display the captured frame

        # Calculate velocities of tracked features
        microsphere_frame_data = optical_metrology_module.process_frame_data(frame)
        for microsphere_data in microsphere_frame_data:
            # Log the microsphere ID, velocity, and size in the console
            logging.info(
                f"Microsphere ID: {microsphere_data['id']}, Velocity: {microsphere_data['velocity']:.2f} pixels/frame, Size: {microsphere_data['size']:.2f} pixels")

            # Draw the trajectory of each microsphere
            microsphere_id = microsphere_data["id"]
            if microsphere_id not in colors:
                # Assign a random color if not already assigned
                colors[microsphere_id] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            trajectory = optical_metrology_module.trajectories[microsphere_id]
            for j in range(1, len(trajectory)):
                cv2.line(frame, (int(trajectory[j - 1][0]), int(trajectory[j - 1][1])),
                         (int(trajectory[j][0]), int(trajectory[j][1])), colors[microsphere_id], 2)

        # Display the current frame
        cv2.imshow("Frame", frame)
        # Exit loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close all OpenCV windows
    cam.release()
    out.release()
    cv2.destroyAllWindows()
