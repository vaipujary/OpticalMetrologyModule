import cv2
import os
import numpy as np
import csv
from datetime import datetime
from OpticalMetrologyModule import OpticalMetrologyModule

metrology_module = OpticalMetrologyModule(parent_ui=None)

lk_params = dict(winSize=(20, 20),
                 maxLevel=4,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Parameters for goodFeaturesToTrack
feature_params = dict(maxCorners=5,  # adjust based on density of particles
                      qualityLevel=0.4,  # adjust based on quality of video
                      minDistance=300,
                      blockSize=7)
# Initialize variables
cap = cv2.VideoCapture("../Test Data/Videos/MicrosphereVideo3.avi")
ret, old_frame = cap.read()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
id_mapping = {}
next_particle_id = 0  # Counter for unique particle IDs
frame_count = 0

def track_particles(frame):
    global id_mapping, next_particle_id, frame_count, old_gray, p0

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    new_p0 = []
    new_id_mapping = {}
    results = []
    used_particle_ids = set()

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

                        size = metrology_module.calculate_size(frame, (a,b), particle_id)  # Calculate size using new coordinates.
                        print(f"Particle ID: {particle_id}, Size: {size}")
                        if size is not None:
                            size_um = (size / 23.269069947552367) * 1000
                            velocity = metrology_module.calculate_velocity(a, b, c, d)  # Calculate velocity
                            velocity_mm_per_s = velocity / 23.269069947552367

                            new_id_mapping[tuple(new.flatten())] = particle_id  # Update id mapping with NEW coordinates.

                            x_mm = a / 23.269069947552367
                            y_mm = b / 23.269069947552367

                            # print(f"Results: particle id: {particle_id}, size: {size_um}, velocity: {velocity_mm_per_s}")

                            results.append({  # Append the result directly
                                "frame_number": frame_count,
                                "particle_id": particle_id,
                                "x": x_mm,
                                "y": y_mm,
                                "size": size_um,
                                "velocity": velocity_mm_per_s
                            })

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

                    id_mapping[(a, b)] = particle_id

                    if p0 is not None:
                        p0 = np.vstack((p0, new.reshape(-1, 1, 2)))
                    else:
                        p0 = new.reshape(-1, 1, 2)

    frame_count += 1
    old_gray = frame_gray.copy()

    return results

def analyze_video_at_fps(video_path, fps_multiplier=1.0, debug=False):
    """Analyzes particle sizes in a video at adjustable frame rates."""
    global frame_count
    max_frames = 1000
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if not cap.isOpened():
        raise IOError(f"Could not open video: {video_path}")

    original_fps = cap.get(cv2.CAP_PROP_FPS)
    adjusted_fps = original_fps * fps_multiplier

    if debug:  # Only create CSV file and writer if debug is True
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        csv_filename = f"size_video_analysis_{adjusted_fps:.2f}fps_{timestamp}.csv"

        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['frame_number', 'particle_id', 'x', 'y', 'size', 'velocity']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                results = track_particles(frame)

                print(f"Frame {frame_count}: {len(results)} particles tracked")
                for result in results:
                    writer.writerow(result)
                    particle_id = result['particle_id']
                    size = result['size']
                    velocity = result['velocity']
                    print(f"Particle ID: {particle_id}, Size: {size:.2f} microns, Velocity: {velocity:.2f} mm/s")

                cv2.imshow('Video Analysis', frame)

                if cv2.waitKey(int(1000 / adjusted_fps)) & 0xFF == ord('q'):
                    break
    else:  # Run the analysis without logging if debug is not True
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = track_particles(frame)

            print(f"Frame {frame_count}: {len(results)} particles tracked")
            for result in results:
                particle_id = result['particle_id']
                size = result['size']
                velocity = result['velocity']
                print(f"Particle ID: {particle_id}, Size: {size:.2f} microns, Velocity: {velocity:.2f} mm/s")

            cv2.imshow('Video Analysis', frame)

            if cv2.waitKey(int(1000 / adjusted_fps)) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_file = "../Test Data/Videos/MicrosphereVideo3.avi"  # Replace with your actual video path
    try:
        analyze_video_at_fps(video_file, fps_multiplier=8, debug=True)
    except Exception as e:
        print(f"An error occurred: {e}")
