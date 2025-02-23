import cv2
import numpy as np
import random

def display_trajectories(video_path, trajectory_length=30):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file.")
        return

    # Parameters for Lucas-Kanade optical flow
    lk_params = dict(winSize=(20, 20),
                     maxLevel=4,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    # Parameters for goodFeaturesToTrack
    feature_params = dict(maxCorners=5, # adjust based on density of particles
                          qualityLevel=0.4, # adjust based on quality of video
                          minDistance=300,
                          blockSize=7)

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

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = np.zeros_like(frame)

        new_p0 = []
        new_id_mapping = {}

        if p0 is not None:
            p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

            if p1 is not None:
                for i, (new, old) in enumerate(zip(p1, p0)):
                    a, b = new.ravel()
                    c, d = old.ravel()
                    particle_id = id_mapping.get(tuple(old.ravel()))  # Retrieve particle ID

                    if particle_id is not None and st[i, 0] == 1:  # Check tracking status
                        new_id_mapping[(a, b)] = particle_id  # Update ID mapping
                        new_p0.append(new)  # Keep point for next frame

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
                        particle_id = next_particle_id
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
        cv2.imshow('frame', img)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

        # Update the previous frame
        old_gray = frame_gray.copy()

    cv2.destroyAllWindows()
    cap.release()


# Example usage (replace with your video file path)
video_path = "../Test Data/Videos/MicrosphereVideo3.avi"
display_trajectories(video_path, trajectory_length=30)

#Contours?

#
# contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
# filtered_contours = []
# for contour in contours:
#     x, y, w, h = cv2.boundingRect(contour)
#     aspect_ratio = float(w) / h
#     if 0.67 <= aspect_ratio <= 1.5:  # Example: filter for aspect ratios close to 1 (adjust as needed)
#         filtered_contours.append(contour)
# mask = np.zeros_like(frame_gray)
# cv2.drawContours(mask, filtered_contours, -1, (255, 255, 255), -1)
#
# mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

# def display_trajectories(video_path, trajectory_length=20):
#     cap = cv2.VideoCapture(video_path)
#     ret, frame = cap.read()
#     if not ret:
#         print("Error opening video file.")
#         return
#
#     # Initialize variables for tracking
#     lk_params = dict(winSize=(15, 15),
#                      maxLevel=2,
#                      criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
#
#     # Create some random colors for the trajectories
#     colors = np.random.randint(0, 255, (100, 3))
#
#     # Take first frame and find corners in it
#     old_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
#
#     # Store trajectories for each point
#     trajectories = {}
#     next_trajectory_index = 0  # Keep track of next available index
#
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#
#         frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#         # Calculate optical flow
#         p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
#
#         # Create a new mask for each frame
#         mask = np.zeros_like(frame)
#
#         # Before filtering, store the indices of good points
#         good_indices = np.where(st == 1)[0]
#
#         # Select good points and remove points that have moved off-screen
#         if p1 is not None:
#             good_new = p1[st == 1]
#             good_old = p0[st == 1]
#
#             # Filter out points that are outside the frame boundaries
#             h, w = frame.shape[:2]
#             inside_frame = lambda pt: 0 <= pt[0] < w and 0 <= pt[1] < h
#             inside_indices = [i for i, new in enumerate(good_new.reshape(-1, 2)) if inside_frame(new)]
#
#             good_new = good_new[inside_indices]
#             good_old = good_old[inside_indices]
#
#             for i, (new, old) in enumerate(zip(good_new, good_old)):
#                 a, b = new.ravel()
#                 c, d = old.ravel()
#
#                 # Get the original trajectory index from before filtering
#                 original_index = good_indices[inside_indices[i]]
#
#                 if original_index not in trajectories:
#                     trajectories[original_index] = []
#                 trajectories[original_index].append((int(a), int(b)))
#                 if len(trajectories[original_index]) > trajectory_length:
#                     trajectories[original_index].pop(0)
#
#                 for k in range(1, len(trajectories[original_index])):
#                     mask = cv2.line(mask, trajectories[original_index][k - 1], trajectories[original_index][k],
#                                     colors[original_index % len(colors)].tolist(), 2)
#                 frame = cv2.circle(frame, (int(a), int(b)), 5, colors[original_index % len(colors)].tolist(), -1)
#
#
#         img = cv2.add(frame, mask)
#
#         cv2.imshow('frame', img)
#         k = cv2.waitKey(30) & 0xff
#         if k == 27:
#             break
#
#         # Now update the previous frame and previous points
#         old_gray = frame_gray.copy()
#         p0 = good_new.reshape(-1, 1, 2)
#         if p0 is None or p0.size == 0:
#             p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, maxCorners=100, qualityLevel=0.3, minDistance=7,
#                                          blockSize=7)
#             if p0 is None:
#                 print("Error tracking good features.")
#                 break
#
#             trajectories = {}  # Clear trajectories when new features are tracked
#
#     cv2.destroyAllWindows()
#     cap.release()
#
#
# # Example usage
# video_path = "../Test Data/Videos/MicrosphereVideo3.avi"
# display_trajectories(video_path, trajectory_length=50)

