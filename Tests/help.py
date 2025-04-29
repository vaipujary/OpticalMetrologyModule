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

    # # # Generate random colors for trajectories
    # def get_random_color():
    #     return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    #
    # colors = [get_random_color() for _ in range(100)]

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
                                     (0, 255, 0), 1)
#colors[particle_id % len(colors)]
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
                        #
                        # if particle_id >= len(colors):
                        #     colors.append(get_random_color())

                        trajectories[particle_id] = [(a, b)]
                        id_mapping[(a, b)] = particle_id

                        if p0 is not None:
                            p0 = np.vstack((p0, new.reshape(-1, 1, 2)))
                        else:
                            p0 = new.reshape(-1, 1, 2)

        frame_count += 1
        img = cv2.add(frame, mask)
        cv2.imshow('Video with Real-time Trajectories', img)
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



