import matplotlib

matplotlib.use('TkAgg')


import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cv2
import random
from OpticalMetrologyModule import OpticalMetrologyModule
from VideoProcessor import VideoProcessor
import os  # import os module
import numpy as np
import time

VIDEO_SOURCE = "../Test Data/Videos/MicrosphereVideo3.avi"  # Path to your video file

# Initialize metrology module, capture, and plotting elements
metrology_module = OpticalMetrologyModule(parent_ui=None)
video_processor = VideoProcessor(ui_video_label=None, input_mode="file", video_source=VIDEO_SOURCE)

# Check if the video file exists
if not os.path.exists(VIDEO_SOURCE):
    print(f"Error: Video file not found at {VIDEO_SOURCE}")
    exit()  # Exit if the file doesn't exist

cap = cv2.VideoCapture(VIDEO_SOURCE)  # Initialize video capture

# Check if video opened successfully
if not cap.isOpened():
    print(f"Error: Could not open video source: {VIDEO_SOURCE}")
    exit()  # Exit if video cannot be opened

# Get the total number of frames
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

if total_frames <= 0:  # Check if frame count is valid
    print("Error: Invalid frame count. Video might be corrupt.")
    exit()

# Cap the number of frames for now to test
max_frames = 100

fig, (ax1, ax2) = plt.subplots(2, 1)
particle_ids = []
size_data = []
velocity_data = []
line1, = ax1.plot(particle_ids, size_data)
line2, = ax2.plot(particle_ids, velocity_data)

# Parameters for Lucas-Kanade optical flow
lk_params = dict(winSize=(20, 20),
                 maxLevel=4,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Parameters for goodFeaturesToTrack
feature_params = dict(maxCorners=5,  # adjust based on density of particles
                      qualityLevel=0.4,  # adjust based on quality of video
                      minDistance=300,
                      blockSize=7)

scatter1 = None  # Initialize scatter1 and scatter2
scatter2 = None

# Initialize variables (correct frame reading)
ret, frame = cap.read()  # Read first frame here
if not ret:
    print("Error: Could not read the first frame.")
    exit()

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Initialize with grayscale

# # Generate random colors for trajectories
def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

colors = [get_random_color() for _ in range(100)]
# colors = np.random.randint(0, 255, (100, 3))

# Initialize variables
ret, old_frame = cap.read()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
trajectories = {}  # Dictionary to store trajectories for each particle
id_mapping = {}  # Dictionary to map points to unique particle IDs
next_particle_id = 0  # Counter for unique particle IDs
frame_count = 0

def init():
    ax1.set_xlabel("Particle ID")
    ax1.set_ylabel("Size (microns)")
    ax2.set_xlabel("Particle ID")
    ax2.set_ylabel("Velocity (mm/s)")
    return line1, line2

def track_and_display_particles(frame):
    global old_gray, p0, id_mapping, frame_count, next_particle_id, trajectories

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(frame)

    new_p0 = []
    new_id_mapping = {}
    results = []
    used_particle_ids = set()
    trajectory_length = 30

    if p0 is not None:
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

        if p1 is not None:

            for new, old, status in zip(p1, p0, st):
                if status:
                    a, b = new.ravel()
                    c, d = old.ravel()
                    prev_key = tuple(old.ravel())
                    particle_id = id_mapping.get(prev_key)  # Retrieve particle ID

                    if particle_id is not None:  # Check tracking status
                        new_id_mapping[(a, b)] = particle_id  # Update ID mapping
                        new_p0.append(new)  # Keep point for next frame

                        # Handle trajectories
                        if particle_id in trajectories:
                            trajectories[particle_id].append((a, b))
                        else:
                            trajectories[particle_id] = [(a, b)]

                        trajectories[particle_id] = trajectories[particle_id][-trajectory_length:]

                        for k in range(1, len(trajectories[particle_id])):
                            pt1 = trajectories[particle_id][k - 1]
                            pt2 = trajectories[particle_id][k]
                            cv2.line(mask, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])),
                                     colors[particle_id % len(colors)], 1)

                        size = metrology_module.calculate_size(frame, (a,b), particle_id)  # Calculate size using new coordinates.
                        print(f"Particle ID: {particle_id}, Size: {size}")
                        trajectory_mm = []
                        if size is not None:
                            # self.microsphere_sizes[particle_id] = size
                            size_um = (size / 23.269069947552367) * 1000
                            velocity = metrology_module.calculate_velocity(a, b, c, d)  # Calculate velocity
                            velocity_mm_per_s = velocity / 23.269069947552367

                            new_id_mapping[tuple(new.flatten())] = particle_id  # Update id mapping with NEW coordinates.
                            trajectories.setdefault(particle_id, []).append((a, b))  # Update trajectories with NEW coordinates.

                            x_mm = a / 23.269069947552367
                            y_mm = b / 23.269069947552367

                            if particle_id in trajectories:  # Use updated_trajectories
                                for x, y in trajectories[particle_id]:
                                    trajectory_mm.append((x / 23.269069947552367, y / 23.269069947552367))

                            # print(f"Results: particle id: {particle_id}, size: {size_um}, velocity: {velocity_mm_per_s}")

                            results.append({  # Append the result directly
                                "frame_number": frame_count,
                                "particle_id": particle_id,
                                "x": x_mm,
                                "y": y_mm,
                                "size": size_um,
                                "velocity": velocity_mm_per_s,
                                "trajectory": trajectory_mm
                            })
                    else:
                        # Remove lost particles
                        lost_id = id_mapping.pop(tuple(old.ravel()), None)
                        if lost_id is not None:
                            trajectories.pop(lost_id, None)

        p0 = np.array(new_p0).reshape(-1, 1, 2) if new_p0 else None
        id_mapping = new_id_mapping

    # Detect new particles and assign unique IDs
    if frame_count % 10 == 0 or p0 is None:
        kernel = np.ones((5, 5), np.uint8)  # Define the structuring element (adjust size as needed)
        tophat = cv2.morphologyEx(frame_gray, cv2.MORPH_TOPHAT, kernel)
        _, binary = cv2.threshold(tophat, 100, 255, cv2.THRESH_BINARY)

        new_features = cv2.goodFeaturesToTrack(binary, mask=None, **feature_params)

        if new_features is not None:
            for new in new_features:
                a, b = new.ravel()

                if (a, b) not in id_mapping:  # Still check for duplicates
                    while next_particle_id in used_particle_ids:
                        next_particle_id += 1

                    particle_id = next_particle_id
                    used_particle_ids.add(particle_id)
                    next_particle_id += 1

                    if particle_id >= len(colors):
                        colors.append(get_random_color())

                    trajectories[particle_id] = [(a, b)]
                    id_mapping[(a, b)] = particle_id

                    if p0 is not None:
                        p0 = np.vstack((p0, new.reshape(-1, 1, 2)))
                    else:
                        p0 = new.reshape(-1, 1, 2)

    frame_count += 1
    img = cv2.add(frame, mask)
    old_gray = frame_gray.copy()

    return img, results

def animate(i):
    global particle_ids, size_data, velocity_data, mask, frame_gray, old_gray, p0, id_mapping, trajectories, particle_colors, scatter1, scatter2  # Declare scatter as global

    ret, frame = cap.read()
    if not ret:
        print("End of video reached.")
        ani.event_source.stop()
        return line1, line2  # Return something to prevent error

    output_frame, results = track_and_display_particles(frame)

    if results is None or not isinstance(results, list):
        print(f"Metrology calculations returned None or unexpected type. Skipping frame {i}")
        if scatter1 and scatter2:
            return scatter1, scatter2  # Return existing plots if available.
        return line1, line2  # Return for blitting

    if results:
        for result in results:
            particle_id = result.get('particle_id')
            size = result.get('size')
            velocity = result.get('velocity')
            if all(v is not None for v in [particle_id, size, velocity]):
                particle_ids.append(particle_id)  # Store particle ID
                size_data.append(size)  # Store the particle size
                velocity_data.append(velocity)  # Store the velocity

    # Keep only the last N data points to create a scrolling effect
    scroll_window = 100  # Display the last 50 data points
    if len(particle_ids) > scroll_window:
        particle_ids = particle_ids[-scroll_window:]
        size_data = size_data[-scroll_window:]
        velocity_data = velocity_data[-scroll_window:]

    # Update the scatter plots
    ax1.clear()
    ax2.clear()

    # Update or create scatter plots efficiently
    # if scatter1 is None:  # Initialize only if they don't exist.
    scatter1 = ax1.scatter(particle_ids, size_data, s=30, c='blue', alpha=0.7)
    scatter2 = ax2.scatter(particle_ids, velocity_data, s=30, c='red', alpha=0.7)

    # Dynamically update x-axis limits for scrolling
    x_min = min(particle_ids, default=0) - 1
    x_max = max(particle_ids, default=1) + 1
    ax1.set_xlim(x_min, x_max)
    ax2.set_xlim(x_min, x_max)

    if size_data:
        y_min_size = min(size_data) - 0.5
        y_max_size = max(size_data) + 0.5
        ax1.set_ylim(y_min_size, y_max_size)

    if velocity_data:
        y_min_velocity = min(velocity_data) - 0.5
        y_max_velocity = max(velocity_data) + 0.5
        ax2.set_ylim(y_min_velocity, y_max_velocity)


    cv2.imshow('Camera Feed', output_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        ani.event_source.stop()

    return scatter1, scatter2

ani = animation.FuncAnimation(fig, animate, frames=min(total_frames, max_frames), init_func=init, blit=False, interval=30, cache_frame_data=False)
plt.show()

cap.release()
cv2.destroyAllWindows()
