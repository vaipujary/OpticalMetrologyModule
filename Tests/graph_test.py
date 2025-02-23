import matplotlib

matplotlib.use('TkAgg')


import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cv2
import random
from OpticalMetrologyModule import OpticalMetrologyModule
import os  # import os module
import numpy as np
import time

VIDEO_SOURCE = "../Test Data/Videos/MicrosphereVideo3.avi"  # Path to your video file

# Initialize metrology module, capture, and plotting elements
metrology_module = OpticalMetrologyModule(parent_ui=None)

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
    ax1.set_xlabel("Time (frames)")
    ax1.set_ylabel("Size (microns)")
    ax2.set_xlabel("Time (frames)")
    ax2.set_ylabel("Velocity (mm/s)")
    return line1, line2


def display_trajectories(frame, mask, frame_gray, old_gray, p0, id_mapping, trajectories, next_particle_id, colors,
                         lk_params, feature_params, trajectory_length=30, metrology_module=None):
    print("Inside display_trajectories function")
    new_p0 = []
    new_id_mapping = id_mapping.copy()  # Create a copy of the dictionary
    updated_trajectories = trajectories.copy()

    if p0 is not None:
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

        if p1 is not None:
            good_new = p1[st == 1]
            good_old = p0[st == 1]

            for new, old in zip(good_new, good_old):
                a, b = new.ravel()
                particle_id = id_mapping.get(tuple(old.ravel()))

                if particle_id is not None:
                    new_id_mapping[(a, b)] = particle_id
                    new_p0.append(new)

                    if particle_id in updated_trajectories:
                        updated_trajectories[particle_id].append((a, b))
                    else:
                        updated_trajectories[particle_id] = [(a, b)]

                    updated_trajectories[particle_id] = trajectories[particle_id][-trajectory_length:]

                    for k in range(1, len(updated_trajectories[particle_id])):
                        pt1 = updated_trajectories[particle_id][k - 1]
                        pt2 = updated_trajectories[particle_id][k]
                        cv2.line(mask, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])),
                                 colors[particle_id % len(colors)], 1)

        p0 = np.array(new_p0).reshape(-1, 1, 2) if new_p0 else None

    # Detect new particles and assign unique IDs (only if needed based on your logic. Consider moving to a separate function if used less frequently)
    if frame_count % 10 == 0 or p0 is None:  # Example condition – adjust or remove as needed
        kernel = np.ones((5, 5), np.uint8)
        tophat = cv2.morphologyEx(frame_gray, cv2.MORPH_TOPHAT, kernel)
        _, binary = cv2.threshold(tophat, 100, 255, cv2.THRESH_BINARY)

        new_features = cv2.goodFeaturesToTrack(binary, mask=None, **feature_params)

        if new_features is not None:
            for new in new_features:
                a, b = new.ravel()

                if (a, b) not in id_mapping:
                    particle_id = next_particle_id
                    next_particle_id += 1

                    if particle_id >= len(colors):  # Extend colors if needed
                        colors.append((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

                    updated_trajectories[particle_id] = [(a, b)]
                    new_id_mapping[(a, b)] = particle_id

                    if p0 is not None:
                        p0 = np.vstack((p0, new.reshape(-1, 1, 2)))
                    else:
                        p0 = new.reshape(-1, 1, 2)
        else:
            p0 = None

    metrology_module.trajectories = updated_trajectories  # Update after each frame

    return frame_gray, p0, new_id_mapping, updated_trajectories, next_particle_id, mask


def animate(i):
    global scatter1, scatter2  # Declare scatter as global

    ret, frame = cap.read()
    if not ret:
        print("End of video reached.")
        ani.event_source.stop()
        return line1, line2  # Return something to prevent error

    results = metrology_module.perform_metrology_calculations(frame)  # Call updated function

    if results is None or not isinstance(results, list):
        print(f"Metrology calculations returned None or unexpected type. Skipping frame {i}")
        if scatter1 and scatter2:
            return scatter1, scatter2  # Return existing plots if available.
        return line1, line2  # Return for blitting

    particle_ids = []
    current_frame_sizes = []
    current_frame_velocities = []

    if results:
        for result in results:
            particle_id = result.get('particle_id')
            size = result.get('size')
            velocity = result.get('velocity')
            if particle_id is not None and size is not None and velocity is not None:  # Check for None values.
                particle_ids.append(particle_id)
                current_frame_sizes.append(size)
                current_frame_velocities.append(velocity)

    # Update or create scatter plots efficiently
    if scatter1 is None:  # Initialize only if they don't exist.
        scatter1, = ax1.plot(particle_ids, current_frame_sizes, 'o', c='blue')
        scatter2, = ax2.plot(particle_ids, current_frame_velocities, 'x', c='red')
    else:
        if particle_ids and current_frame_sizes and current_frame_velocities:  # check if there are any results to use for updates
            scatter1.set_data(particle_ids, current_frame_sizes)
            scatter2.set_data(particle_ids, current_frame_velocities)

    # global old_gray, p0, id_mapping, trajectories, next_particle_id, frame_count, colors, lk_params, feature_params, scatter1, scatter2
    #
    # ret, frame = cap.read()
    # if not ret:
    #     print("End of video reached.")
    #     ani.event_source.stop()
    #     return line1, line2
    #
    # frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # mask = np.zeros_like(frame)  # Mask for trajectories
    #
    # # Single Optical Flow Calculation
    # if metrology_module.prev_gray is None:
    #     metrology_module.prev_gray = frame_gray
    #     metrology_module.initialize_features(frame.copy(), False)
    #     return line1, line2  # Skip calculations on the very first frame
    #
    # p1, st, err = cv2.calcOpticalFlowPyrLK(
    #     metrology_module.prev_gray, frame_gray, metrology_module.prev_features, None, **metrology_module.lk_params
    # )
    #
    # if p1 is None:  # Handle case where no flow is calculated
    #     print("Optical flow returned None.")
    #     metrology_module.initialize_features(frame_gray.copy(), True)  # Re-initialize features
    #     metrology_module.prev_gray = frame_gray.copy()
    #     return line1, line2  # Return for blitting
    #
    # good_new = p1[st == 1]
    # good_old = metrology_module.prev_features[st == 1]
    #
    # # Update id_mapping and trajectories based on optical flow results
    # new_id_mapping = {}
    # updated_trajectories = {}
    # next_particle_id = 0 if i == 0 else next_particle_id  # Initialize only on first frame
    #
    # for new, old in zip(good_new, good_old):
    #     a, b = new.ravel()
    #     particle_id = id_mapping.get(tuple(old.flatten()))
    #     if particle_id is not None:
    #         new_id_mapping[tuple(new.flatten())] = particle_id  # Use new for id_mapping
    #         updated_trajectories.setdefault(particle_id, []).append((a, b))
    #     else:
    #         particle_id = next_particle_id
    #         next_particle_id += 1
    #     # Now use particle_id (new or existing)
    #     new_id_mapping[tuple(new.flatten())] = particle_id
    #     updated_trajectories.setdefault(particle_id, []).append((a, b))
    #
    # id_mapping = new_id_mapping
    # metrology_module.trajectories = updated_trajectories
    # metrology_module.prev_features = good_new.reshape(-1, 1, 2)
    # metrology_module.prev_gray = frame_gray.copy()
    #
    # # Draw trajectories
    # for particle_id, trajectory in updated_trajectories.items():
    #     metrology_module.trajectories[particle_id] = trajectory[-30:]  # Keep only last 30 points
    #     for k in range(1, len(trajectory)):
    #         pt1 = trajectory[k - 1]
    #         pt2 = trajectory[k]
    #         cv2.line(mask, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])),
    #                  colors[particle_id % len(colors)], 2)
    #
    # p0 = good_new.reshape(-1, 1, 2)
    #
    # frame_count += 1
    # metrology_module.frame_number = i
    # results = metrology_module.perform_metrology_calculations(frame, metrology_module.trajectories,
    #                                                           metrology_module.scaling_factor,
    #                                                           id_mapping)
    #
    # if results is None:  # Check if results is None
    #     print("Metrology calculations returned None. Skipping this frame.")
    #     if scatter1 is not None and scatter2 is not None:  # check before returning
    #         return scatter1, scatter2  # return even if not updated
    #     return []
    #
    # particle_ids = []
    # current_frame_sizes = []
    # current_frame_velocities = []
    #
    # if isinstance(results, list):  # Check if result is a list and process accordingly.
    #     for result in results:
    #         if result:
    #             particle_id = result.get('particle_id')  # extracting the particle_id from the result dictionary
    #             size = result.get('size')
    #             velocity = result.get('velocity')
    #
    #             if isinstance(size, (int, float, np.number)) and not np.isnan(size) and isinstance(velocity, (
    #                     int, float, np.number)) and not np.isnan(velocity):
    #                 current_frame_sizes.append(size)
    #                 current_frame_velocities.append(velocity)
    #                 particle_ids.append(particle_id)
    # else:
    #     print(f"Frame {i}: Unexpected results type: {type(results)}")
    #     return line1, line2
    #
    # if not particle_ids: # Check for empty results
    #     print(f"Frame {i}: No valid particle IDs found for plotting.")
    #     return []  # return empty list to skip plotting in this frame
    #
    # # Update scatter plot data (more efficient)
    # if scatter1 is None:
    #     scatter1, = ax1.plot(particle_ids, current_frame_sizes, 'o', c='blue')
    #     scatter2, = ax2.plot(particle_ids, current_frame_velocities, 'x', c='red')
    # else:
    #     scatter1.set_data(particle_ids, current_frame_sizes)
    #     scatter2.set_data(particle_ids, current_frame_velocities)
    #
    # ax1.set_xlabel("Particle ID")
    # ax1.set_xlim(-1, len(results))
    #
    # if current_frame_sizes:
    #     ymin = min(current_frame_sizes)
    #     ymax = max(current_frame_sizes)
    #     if ymin == ymax:  # Check if min and max are equal
    #         ymin -= 0.5  # Expand the range slightly
    #         ymax += 0.5
    #     ax1.set_ylim(ymin, ymax)
    #
    # ax2.set_xlabel("Particle ID")
    # ax2.set_xlim(-1, len(results))  # Adjust x-axis limits for particle IDs
    # if current_frame_velocities:
    #     ymin = min(current_frame_velocities)
    #     ymax = max(current_frame_velocities)
    #     if ymin == ymax:  # Check if min and max are equal
    #         ymin -= 0.5  # Expand the range slightly
    #         ymax += 0.5
    #     ax2.set_ylim(ymin, ymax)
    #
    # # frame = metrology_module.annotate_frame(frame)
    # cv2.imshow('Camera Feed', frame)
    #
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     ani.event_source.stop()
    #
    # return scatter1, scatter2


ani = animation.FuncAnimation(fig, animate, frames=min(total_frames, max_frames), init_func=init, blit=True, interval=30, cache_frame_data=False)
plt.show()

cap.release()
cv2.destroyAllWindows()

# old_gray, p0, id_mapping, trajectories, next_particle_id, mask = display_trajectories(
#     frame, mask, frame_gray, old_gray, p0, id_mapping, trajectories,
#     next_particle_id, colors, lk_params, feature_params,
#     trajectory_length=30, metrology_module=metrology_module  # Pass metrology_module
# )
# frame_count += 1
#
# metrology_module.frame_number = i
#
# print(f"Frame {i}: Number of Trajectories = {len(trajectories)}")
#
# # Correct call to perform_metrology_calculations
# results = metrology_module.perform_metrology_calculations(frame, trajectories, metrology_module.scaling_factor, id_mapping)
