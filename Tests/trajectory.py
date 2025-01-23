import cv2
import numpy as np
import matplotlib.pyplot as plt
import trackpy as tp
import pandas as pd

# Step 1: Load the video
video_path = '../Test Data/Videos/5.gif'  # Replace this with the path to your video
cap = cv2.VideoCapture(video_path)

# Extract frames and convert to grayscale
frames = []
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frames.append(gray_frame)

cap.release()

# Step 2: Preprocess frames and detect particles
# Trackpy expects images to be in 2D numpy arrays
# Adjust `diameter` to fit the size of your particles
particle_diameter = 11  # Parameter for particle detection (adjust as needed)
f = tp.batch(frames, diameter=particle_diameter, minmass=100)

# Step 3: Link particles to create trajectories
# Linking positions across frames into trajectories
t = tp.link_df(f, search_range=15, memory=3)

# Step 4: Visualize trajectories
# Plot the trajectories using matplotlib
plt.figure(figsize=(8, 6))
tp.plot_traj(t)
plt.title('Particle Trajectories')
plt.xlabel('X position')
plt.ylabel('Y position')
plt.show()

# Step 5: Overlay trajectories on video (Optional)
# Let's overlay the trajectories frame by frame on the original video
output_video_path = 'output_with_trajectories.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
frame_height, frame_width = frames[0].shape
out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (frame_width, frame_height), isColor=True)

# Iterate through each frame and draw trajectories
for frame_idx, frame in enumerate(frames):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)  # Convert to RGB for visualization
    # Get trajectories for this frame
    frame_data = t[t['frame'] == frame_idx]
    for _, row in frame_data.iterrows():
        x, y = int(row['x']), int(row['y'])
        particle_id = int(row['particle'])  # Unique particle ID
        # Assign a color based on particle ID
        color = tuple((np.random.randint(0, 255) for _ in range(3)))
        cv2.circle(frame_rgb, (x, y), 6, color, -1)  # Draw particle
        cv2.putText(frame_rgb, str(particle_id), (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    out.write(frame_rgb)

out.release()
print(f'Trajectory video saved to {output_video_path}')
