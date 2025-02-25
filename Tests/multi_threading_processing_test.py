import multiprocessing as mp
import threading
import queue
import cv2
import matplotlib
from matplotlib import animation
matplotlib.use('TkAgg')
# matplotlib.use('agg')
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import matplotlib.pyplot as plt
import time
import csv
import numpy as np
import datetime
from OpticalMetrologyModule import OpticalMetrologyModule

# Initialize video capture
cap = cv2.VideoCapture("../Test Data/Videos/MicrosphereVideo3.avi")

# Parameters for Lucas-Kanade optical flow
lk_params = dict(winSize=(20, 20),
                 maxLevel=4,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Parameters for goodFeaturesToTrack
feature_params = dict(maxCorners=5,  # adjust based on density of particles
                      qualityLevel=0.4,  # adjust based on quality of video
                      minDistance=300,
                      blockSize=7)

# Initialize variables
ret, old_frame = cap.read()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
id_mapping = {}
next_particle_id = 0  # Counter for unique particle IDs
frame_count = 0
mask = None
# particle_data = {}
trajectories = {}

# Lock for thread safety within each process
dict_lock = threading.Lock()

metrology_module = OpticalMetrologyModule(parent_ui=None, debug=False)

def capture_frames(cap, frame_queue, display_queue):
    """Capture video frames continuously and place them in the queue."""
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Place the frame in both the processing and display queues
        try:
            frame_queue.put_nowait(frame)
        except queue.Full:
            pass  # Drop the frame if the queue is full (avoid stalling)

        try:
            display_queue.put_nowait(frame.copy())
        except queue.Full:
            pass  # Ensure video display is not stalled


# Thread to display video trajectories
def display_results(display_queue, trajectory_length=30):
    """Display original frames with trajectory overlays."""
    # Use a persistent mask for smooth trajectory display
    global mask, p0, old_gray, id_mapping, frame_count, next_particle_id, trajectories

    while True:
        if not display_queue.empty():
            frame = display_queue.get()
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Initialize mask or resize if needed
            mask = np.zeros_like(frame)

            new_p0, new_id_mapping = [], {}

            # Perform minimal trajectory overlay processing
            if p0 is not None:
                p1, st, _ = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

                if p1 is not None:
                    for i, (new, old) in enumerate(zip(p1, p0)):
                        a, b = new.ravel()
                        particle_id = id_mapping.get(tuple(old.ravel()))  # Retrieve particle ID

                        if particle_id is not None and st[i, 0] == 1:  # Check tracking status
                            new_id_mapping[(a, b)] = particle_id  # Update ID mapping
                            new_p0.append(new)  # Keep point for next frame

                            if particle_id in trajectories:
                                trajectories[particle_id].append((a, b))
                                trajectories[particle_id] = trajectories[particle_id][-trajectory_length:]
                                for k in range(1, len(trajectories[particle_id])):
                                    pt1 = trajectories[particle_id][k - 1]
                                    pt2 = trajectories[particle_id][k]
                                    cv2.line(mask, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])),
                                             (0, 255, 0), 1)
                            else:
                                trajectories[particle_id] = [(a, b)]

                p0 = np.array(new_p0).reshape(-1, 1, 2) if new_p0 else None
                id_mapping = new_id_mapping

            # Detect new particles and assign unique IDs
            if frame_count % 5 == 0 or p0 is None:
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

                            trajectories[particle_id] = [(a, b)]
                            id_mapping[(a, b)] = particle_id

                            if p0 is not None:
                                p0 = np.vstack((p0, new.reshape(-1, 1, 2)))
                            else:
                                p0 = new.reshape(-1, 1, 2)

            frame_count += 1
            img = cv2.add(frame, mask)

            cv2.imshow('Video with Real-Time Trajectories', img)

            # Update the previous frame
            old_gray = frame_gray.copy()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

def update_graph(data_queue):
    """Continuously update real-time scatter plots for particle size and velocity."""
    # Initialize PyQtGraph application
    app = QtWidgets.QApplication([])

    # Create a main window to hold plots
    win = pg.GraphicsLayoutWidget(show=True, title="Real-Time Particle Size and Velocity")
    win.resize(800, 600)
    win.setWindowTitle('Real-Time Particle Size and Velocity')

    # Create two plots for size and velocity
    size_plot = win.addPlot(title="Particle Sizes (microns)")
    size_plot.setLabel('left', 'Size (microns)')
    size_plot.setLabel('bottom', 'Particle ID')
    size_plot.showGrid(x=True, y=True)

    win.nextRow()  # Add the second plot below the first

    velocity_plot = win.addPlot(title="Particle Velocities (mm/s)")
    velocity_plot.setLabel('left', 'Velocity (mm/s)')
    velocity_plot.setLabel('bottom', 'Particle ID')
    velocity_plot.showGrid(x=True, y=True)

    # Initialize scatter plots
    size_scatter = size_plot.plot([], [], pen=None, symbol='o', symbolBrush='blue', name="Size")
    velocity_scatter = velocity_plot.plot([], [], pen=None, symbol='x', symbolBrush='red', name="Velocity")

    # Initialize data storage
    particle_ids, sizes, velocities = [], [], []

    # Update function for PyQtGraph
    def update_plots():
        nonlocal particle_ids, sizes, velocities
        print(f"Queue size: {data_queue.qsize()}")
        # Fetch data from the data queue
        while not data_queue.empty():
            try:
                _, pid, size, velocity, _ = data_queue.get_nowait()
                '''print(f"Data received: Particle ID={pid}, Size={size}, Velocity={velocity}")'''

                # Validate and sanitize the data before updating lists
                if isinstance(pid, int) and isinstance(size, (int, float)) and isinstance(velocity, (float, np.float32, np.float64)):
                    if pid not in particle_ids:
                        particle_ids.append(pid)
                        sizes.append(size)
                        velocities.append(velocity)
                    else:
                        # Update data lists. Find the right index to insert or update values based on existing particle_ids
                        index = particle_ids.index(pid)
                        sizes[index] = size
                        velocities[index] = velocity

                        # print(f"Added data: PID={pid}, Size={size}, Velocity={velocity}")
            except queue.Empty:
                '''print("Data queue is empty.")'''
                pass

        # Dynamically update X-axis range based on particle IDs
        if len(particle_ids) > 0 and len(sizes) > 0 and len(velocities) > 0:
            # Update the scatter plot data
            size_scatter.setData(particle_ids, sizes)
            velocity_scatter.setData(particle_ids, velocities)

            max_pid = max(particle_ids) + 1
            size_plot.setXRange(0, max_pid)
            velocity_plot.setXRange(0, max_pid)
        else:
            '''print("No valid data to plot.")'''


    # Use a QTimer to schedule periodic updates
    timer = QtCore.QTimer()
    timer.timeout.connect(update_plots)  # Call the `update_plots` function periodically
    timer.start(200)  # Update every 100 milliseconds

    # Start the PyQtGraph application
    QtWidgets.QApplication.instance().exec()


def write_csv(data_queue, csv_filename, csv_lock, batch_size=100):
    """Write particle size and velocity data to CSV."""
    with open(csv_filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Frame Number', 'Timestamp', 'Particle ID', 'Size (microns)', 'Velocity (mm/s)', 'Trajectory'])

        batch = []
        while True:
            try:
                frame_number, particle_id, size, velocity, trajectory = data_queue.get()
                data_queue.get(timeout=1)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Get the current timestamp

                if trajectory is not None and len(trajectory) > 0:
                    trajectory_str = ";".join([f"({int(x)}, {int(y)})" for x, y in trajectory])
                else:
                    trajectory_str = None

                batch.append([frame_number, timestamp, particle_id, size, velocity, trajectory_str])

                # Write batch to avoid frequent disk writes
                if len(batch) >= batch_size:
                    with csv_lock:
                        csvwriter.writerows(batch)
                        # print("Inside CSV lock!")
                        # if size is not None and velocity is not None and trajectory_str is not None:
                        #     print("Writing to CSV")
                        #     csvwriter.writerow([frame_number, timestamp, particle_id, size, velocity, trajectory_str])
                        csvfile.flush() # Ensure data is written immediately
                        batch = []
            except queue.Empty:
                time.sleep(0.1)  # Reduce resource competition by pausing slightly
                # print("CSV queue is empty.")
                pass

def track_particles(frame, particle_data):
    global old_gray, p0, id_mapping, frame_count, next_particle_id

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

                        # Handle trajectories
                        if particle_id in particle_data:
                            trajectory = list(particle_data[particle_id]["trajectory"])
                            trajectory.append((a, b))
                            particle_data[particle_id]["trajectory"] = trajectory  # Update trajectory back

                        else:
                            particle_data[particle_id] = {"size": None, "velocity": None, "trajectory": [(a, b)]}

                        # Keep only the last 30 points in the trajectory
                        particle_data[particle_id]["trajectory"] = particle_data[particle_id]["trajectory"][-30:]
                        size = metrology_module.calculate_size(frame, (a,b), particle_id)  # Calculate size using new coordinates.
                        velocity = metrology_module.calculate_velocity(a, b, c, d)  # Calculate velocity
                        trajectory_mm = []

                        size_um = (size / 23.269069947552367) * 1000 if size is not None else None
                        velocity_mm_per_s = velocity / 23.269069947552367 if velocity is not None else None

                        # print(f"Particle ID: {particle_id}, Size: {size_um}, Velocity: {velocity_mm_per_s} mm/s")
                        new_id_mapping[tuple(new.flatten())] = particle_id  # Update id mapping with NEW coordinates.

                        # Convert trajectory to millimeters
                        for x, y in particle_data[particle_id]["trajectory"]:
                            trajectory_mm.append((x / 23.269069947552367, y / 23.269069947552367))

                        # print(f"Detected particle: ID={particle_id}, Size={size_um}, Velocity={velocity_mm_per_s}")

                        results.append({  # Append the result directly
                            "frame_number": frame_count,
                            "particle_id": particle_id,
                            "size": size_um,
                            "velocity": velocity_mm_per_s,
                            "trajectory": trajectory_mm
                        })
                    # else:
                    #     # Remove lost particles
                    #     lost_id = id_mapping.pop(tuple(old.ravel()), None)
                    #     if lost_id is not None:
                    #         parti.pop(lost_id, None)

        p0 = np.array(new_p0).reshape(-1, 1, 2) if new_p0 else None
        id_mapping = new_id_mapping

    # Detect new particles and assign unique IDs
    if frame_count % 5 == 0 or p0 is None:
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

                    # Initialize particle data
                    particle_data[particle_id] = {"size": None, "velocity": None, "trajectory": [(a, b)]}

                    id_mapping[(a, b)] = particle_id

                    if p0 is not None:
                        p0 = np.vstack((p0, new.reshape(-1, 1, 2)))
                    else:
                        p0 = new.reshape(-1, 1, 2)

    frame_count += 1
    old_gray = frame_gray.copy()

    return results

def process_frame_worker(frame_queue, data_queue, particle_data):
    """Process frames from the frame queue and log particle size and velocity data."""
    frame_number = 0
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            # Start timing the frame processing
            start_time = time.time()

            results = track_particles(frame, particle_data)

            # End timing the frame processing
            end_time = time.time()

            # Calculate and log the processing time
            processing_time = end_time - start_time
            print(f"Time taken to process frame {frame_number}: {processing_time:.4f} seconds")

            if not results:  # Log empty results for debugging
                '''print(f"No particles detected in frame {frame_number}")'''

            else:
                # print(f"Processed {len(results)} particles for frame.")
                with dict_lock:
                    for result in results:
                        particle_id = result["particle_id"]
                        size = result["size"]
                        velocity = result["velocity"]
                        trajectory = result["trajectory"]

                        # Update shared particle data
                        particle_data[particle_id] = {
                            "size": size,
                            "velocity": velocity,
                            "trajectory": trajectory
                        }

                        # Store data in queue for CSV logging
                        # print(
                            # f"Adding data to queue: frame={frame_number}, particle_id={particle_id}, size={size}, velocity={velocity}")
                        data_queue.put((frame_number, particle_id, size, velocity, trajectory))

            frame_number += 1

if __name__ == "__main__":
    # Shared multiprocessing manager
    manager = mp.Manager()  # Initialize Manager for multiprocessing-safe dictionary
    particle_data = manager.dict()  # Shared across all processes
    csv_lock = threading.Lock()  # Prevent race conditions when writing to CSV

    # Queues for inter-process communication
    frame_queue = mp.Queue(maxsize=500)  # Stores raw frames
    data_queue = mp.Queue()  # Stores size and velocity data for logging and graphing
    display_queue = mp.Queue(maxsize=500) # Holds display frames

    # CSV file setup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"particle_data_{timestamp}.csv"

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Start capture thread
    capture_thread = threading.Thread(target=capture_frames, args=(cap, frame_queue, display_queue), daemon=True)
    capture_thread.start()

    num_processes = mp.cpu_count() - 1

    process_pool = [
        mp.Process(target=process_frame_worker, args=(frame_queue, data_queue, particle_data), daemon=True)
        for _ in range(num_processes)
    ]

    # Wait for processes to complete
    for p in process_pool:
        p.start()

    csv_thread = threading.Thread(target=write_csv, args=(data_queue, csv_filename, csv_lock), daemon=True)
    csv_thread.start()

    display_thread = threading.Thread(target=display_results, args=(display_queue,), daemon=True)
    display_thread.start()
    graph_thread = threading.Thread(target=update_graph, args=(data_queue,), daemon=True)
    graph_thread.start()

    # Main loop to monitor and shutdown properly
    try:
        # Wait for threads and processes
        capture_thread.join()
        display_thread.join()

        for process in process_pool:
            process.join()

        graph_thread.join()
        csv_thread.join()

    except KeyboardInterrupt:
        '''print("\nShutting down gracefully...")'''
    finally:
        # Ensure all resources are released
        cap.release()
        cv2.destroyAllWindows()
