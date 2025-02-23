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
            # good_new = p1[st == 1]  # Get only the good new points
            # good_old = p0[st == 1]
            # print(f"good new: {good_new}, good old: {good_old}")
            # Handle if features are lost
            # if not good_new.any() or not good_old.any():
            #     print("All features lost. Re-initializing.")

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
    global size_data, velocity_data, mask, frame_gray, old_gray, p0, id_mapping, trajectories, particle_colors, scatter1, scatter2  # Declare scatter as global

    ret, frame = cap.read()
    if not ret:
        print("End of video reached.")
        ani.event_source.stop()
        return line1, line2  # Return something to prevent error

    # output_frame, frame_gray, p0, particle_colors, id_mapping, _ = video_processor.track_particles(frame, trajectories, particle_colors, id_mapping)

    output_frame, results = track_and_display_particles(frame)
    # old_gray = frame_gray.copy()  # Now old_gray will contain the latest grayscale frame.
    # video_processor.old_gray = frame_gray.copy()  # Now the video_processor also has the correct old_gray value.
    #
    # output_frame = video_processor.display_trajectories(output_frame, id_mapping, video_processor.trajectories,
    #                                                     particle_colors)
    #
    # results = metrology_module.perform_metrology_calculations(frame, id_mapping)  # Call updated function

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

    # Update or create scatter plots efficiently
    if scatter1 is None:  # Initialize only if they don't exist.
        scatter1, = ax1.plot(particle_ids, size_data, 'o', c='blue')
        scatter2, = ax2.plot(particle_ids, velocity_data, 'x', c='red')
    else:
        scatter1.set_data(particle_ids, size_data)
        scatter2.set_data(particle_ids, velocity_data)

    # Dynamic x-axis limits for scrolling effect
    if particle_ids:  # Check if any particles are being tracked
        x_max = max(particle_ids)
        x_min = 0  # Start at 0 or adjust if there are any lost particles
        ax1.set_xlim(x_min, x_max)
        ax2.set_xlim(x_min, x_max)

    if size_data:
        ax1.set_ylim(min(size_data) - 0.5, max(size_data) + 0.5)  # Dynamic Y limits
    if velocity_data:
        ax2.set_ylim(min(velocity_data) - 0.5, max(velocity_data) + 0.5)  # Dynamic Y limits

    cv2.imshow('Camera Feed', output_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        ani.event_source.stop()

    return scatter1, scatter2

    # updated_trajectories = trajectories.copy()
    #
    # if p0 is not None:
    #     for particle_id, points in updated_trajectories.items():  # Use updated_trajectories directly
    #         if len(points) > 1:  # Draw the trajectories only if there are points.
    #             for k in range(1, len(points)):
    #                 pt1 = points[k - 1]
    #                 pt2 = points[k]
    #                 cv2.line(mask, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])),
    #                          colors[particle_id % len(colors)], 1)
    #
    # return mask
    #
    # new_p0 = []
    # new_id_mapping = id_mapping.copy()  # Create a copy of the dictionary
    # updated_trajectories = trajectories.copy()
    #
    # # Handle existing particles
    # if p0 is not None:
    #     p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    #
    #     if p1 is not None:
    #         good_new = p1[st == 1]
    #         good_old = p0[st == 1]
    #
    #         for new, old in zip(good_new, good_old):
    #             a, b = new.ravel()
    #             particle_id = id_mapping.get(tuple(old.ravel()))
    #             print(f"Particle ID: {particle_id}, (a,b): ({a,b})")
    #             if particle_id is not None:
    #                 new_id_mapping[(a, b)] = particle_id
    #                 new_p0.append(new)
    #
    #                 if particle_id in updated_trajectories:
    #                     updated_trajectories[particle_id].append((a, b))
    #                 else:
    #                     updated_trajectories[particle_id] = [(a, b)]
    #
    #                 updated_trajectories[particle_id] = trajectories[particle_id][-trajectory_length:]
    #
    #                 for k in range(1, len(updated_trajectories[particle_id])):
    #                     pt1 = updated_trajectories[particle_id][k - 1]
    #                     pt2 = updated_trajectories[particle_id][k]
    #                     cv2.line(mask, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])),
    #                              colors[particle_id % len(colors)], 1)
    #
    #     p0 = np.array(new_p0).reshape(-1, 1, 2) if new_p0 else None
    #
    # # Detect new particles and assign unique IDs (only if needed based on your logic. Consider moving to a separate function if used less frequently)
    # if frame_count % 10 == 0 or p0 is None:  # Example condition – adjust or remove as needed
    #     kernel = np.ones((5, 5), np.uint8)
    #     tophat = cv2.morphologyEx(frame_gray, cv2.MORPH_TOPHAT, kernel)
    #     _, binary = cv2.threshold(tophat, 100, 255, cv2.THRESH_BINARY)
    #
    #     new_features = cv2.goodFeaturesToTrack(binary, mask=None, **feature_params)
    #
    #     if new_features is not None:
    #         for new in new_features:
    #             a, b = new.ravel()
    #
    #             if (a, b) not in id_mapping:
    #                 particle_id = next_particle_id
    #                 next_particle_id += 1
    #                 print(f"Particle ID: {particle_id}, (a,b): ({a, b})")
    #
    #                 if particle_id >= len(colors):  # Extend colors if needed
    #                     colors.append((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    #
    #                 updated_trajectories[particle_id] = [(a, b)]
    #                 new_id_mapping[(a, b)] = particle_id
    #
    #                 if p0 is not None:
    #                     p0 = np.vstack((p0, new.reshape(-1, 1, 2)))
    #                 else:
    #                     p0 = new.reshape(-1, 1, 2)
    #     else:
    #         p0 = None
    #
    # metrology_module.trajectories = updated_trajectories  # Update after each frame
    #
    # return frame_gray, p0, new_id_mapping, updated_trajectories, next_particle_id, mask

    #     # # Generate random colors for trajectories
    #     def get_random_color():
    #         return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    #
    #     colors = [get_random_color() for _ in range(100)]
    #     # colors = np.random.randint(0, 255, (100, 3))
    #
    #     # Initialize variables
    #     ret, old_frame = cap.read()
    #     old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    #     p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
    #     trajectories = {}  # Dictionary to store trajectories for each particle
    #     id_mapping = {}  # Dictionary to map points to unique particle IDs
    #     next_particle_id = 0  # Counter for unique particle IDs
    #     frame_count = 0
    #
    #     while True:
    #         ret, frame = cap.read()
    #         if not ret:
    #             break
    #         frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #         mask = np.zeros_like(frame)
    #
    #         new_p0 = []
    #         new_id_mapping = {}
    #
    #
    #         if p0 is not None:
    #             p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    #
    #             if p1 is not None:
    #                 for i, (new, old) in enumerate(zip(p1, p0)):
    #                     a, b = new.ravel()
    #                     c, d = old.ravel()
    #                     particle_id = id_mapping.get(tuple(old.ravel()))  # Retrieve particle ID
    #
    #                     if particle_id is not None and st[i, 0] == 1:  # Check tracking status
    #                         new_id_mapping[(a, b)] = particle_id  # Update ID mapping
    #                         new_p0.append(new)  # Keep point for next frame
    #
    #                         if particle_id in trajectories:
    #                             trajectories[particle_id].append((a, b))
    #                         else:
    #                             trajectories[particle_id] = [(a, b)]
    #
    #                         trajectories[particle_id] = trajectories[particle_id][-trajectory_length:]
    #
    #                         for k in range(1, len(trajectories[particle_id])):
    #                             pt1 = trajectories[particle_id][k - 1]
    #                             pt2 = trajectories[particle_id][k]
    #                             cv2.line(mask, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])),
    #                                      colors[particle_id % len(colors)], 1)
    #
    #             p0 = np.array(new_p0).reshape(-1, 1, 2) if new_p0 else None
    #             id_mapping = new_id_mapping
    #
    #         # Detect new particles and assign unique IDs
    #         if frame_count % 10 == 0 or p0 is None:
    #             kernel = np.ones((5, 5), np.uint8)  # Define the structuring element (adjust size as needed)
    #             tophat = cv2.morphologyEx(frame_gray, cv2.MORPH_TOPHAT, kernel)
    #             _, binary = cv2.threshold(tophat, 100, 255, cv2.THRESH_BINARY)
    #
    #             new_features = cv2.goodFeaturesToTrack(binary, mask=None, **feature_params)
    #
    #             if new_features is not None:
    #                 for new in new_features:
    #                     a, b = new.ravel()
    #
    #                     if (a, b) not in id_mapping:  # Still check for duplicates
    #                         particle_id = next_particle_id
    #                         next_particle_id += 1
    #
    #                         if particle_id >= len(colors):
    #                             colors.append(get_random_color())
    #
    #                         trajectories[particle_id] = [(a, b)]
    #                         id_mapping[(a, b)] = particle_id
    #
    #                         if p0 is not None:
    #                             p0 = np.vstack((p0, new.reshape(-1, 1, 2)))
    #                         else:
    #                             p0 = new.reshape(-1, 1, 2)
    #
    #         frame_count += 1
    #         img = cv2.add(frame, mask)
    #         cv2.imshow('frame', img)
    #         k = cv2.waitKey(30) & 0xff
    #         if k == 27:
    #             break
    #
    #         # Update the previous frame
    #         old_gray = frame_gray.copy()

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
