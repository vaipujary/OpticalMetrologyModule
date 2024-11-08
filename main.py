import cv2
import OpticalMetrologyModule
import time
import logging
import random


# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Capture video from the default camera (camera index 0)
# cap = cv2.VideoCapture(0)
cam = cv2.VideoCapture('/Sample Videos/3.mp4')
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter.fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

optical_metrology_module = OpticalMetrologyModule()

# Get the experiment duration from the user (minimum 10 minutes)
experiment_duration = 10
start_time = time.time()

# Assign random colors to each microsphere for trajectory visualization
colors = {}  # Dictionary to store colors for each microsphere ID

while True:
    # Check if the experiment duration has been reached
    elapsed_time = time.time() - start_time
    if elapsed_time >= experiment_duration:
        logging.info("Experiment time completed.")
        break

    # Read a frame from the video capture
    ret, frame = cam.read()
    if not ret:
        logging.error("Failed to capture image.")
        break

    out.write(frame)
    # Calculate velocities of tracked features
    velocities = optical_metrology_module.calculate_velocity(frame)
    for velocity_data in velocities:
        # Draw the microsphere ID, velocity, and size on the frame
        x, y = velocity_data["position"][0]
        cv2.putText(frame, f"ID: {velocity_data['id']}, Vel: {velocity_data['velocity']:.2f}, Size: {velocity_data['size']:.2f}", (int(x), int(y)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        # Draw the trajectory of each microsphere
        microsphere_id = velocity_data["id"]
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