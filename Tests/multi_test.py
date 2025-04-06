import cv2
import multiprocessing as mp
import threading
import queue
import csv
import numpy as np
import datetime
from collections import deque


# Function for acquiring frames
def acquire_frames(cap, frame_queue, shutdown_event):
    frame_count = 0

    while cap.isOpened() and not shutdown_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (0, 0), fx=0.45, fy=0.45, interpolation=cv2.INTER_AREA)

        try:
            if frame_count % 3 == 0:
                frame_queue.put(frame, block=False)

        except queue.Full:
            pass

        frame_count += 1

    shutdown_event.set() # Signal other processes/threads to stop

# Particle Tracking Thread
def particle_tracking(frame_queue, multiprocessing_queue, shared_dict, dict_lock, shutdown_event):

    try:
        # Get the initial frame from the queue (blocks until available or shutdown_event is set)
        old_frame = frame_queue.get(timeout=2)
    except queue.Empty:
        # If we can't get a frame in time, or if shutting down, exit
        return

    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

    mask = np.zeros_like(old_frame)

    # Parameters for Lucas-Kanade Optical Flow
    lk_params = dict(winSize=(20, 20),
                     maxLevel=4,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.03))

    # Parameters for goodFeaturesToTrack
    feature_params = dict(maxCorners=50,
                          qualityLevel=0.4,
                          minDistance=300,
                          blockSize=7)

    p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

    trajectories = {}  # Dictionary to store particle trajectories
    id_mapping = {}  # Maps positions to particle IDs
    next_particle_id = 0  # Counter for unique particle IDs
    frame_count = 0
    trajectory_length = 30  # Number of frames to store trajectory
    max_particles = 100
    lost_counts = {}

    while not shutdown_event.is_set():

        frame = frame_queue.get()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        mask.fill(0)

        new_p0 = []
        new_id_mapping = {}

        # Mark all known particles as "lost" until proven otherwise this frame
        for pid in list(lost_counts.keys()):
            lost_counts[pid] += 1

        if p0 is not None:
            p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, gray, p0, None, **lk_params)

            if p1 is not None:
                for i, (new, old) in enumerate(zip(p1, p0)):
                    a, b = new.ravel()
                    c, d = old.ravel()

                    # If old position is recognized, track continuity
                    if (c, d) in id_mapping:
                        pid = id_mapping[(c, d)]
                        new_id_mapping[(a, b)] = pid

                    # Retrieve or assign a particle ID
                    particle_id = id_mapping.get((c, d))
                    if particle_id is not None and st[i, 0] == 1:
                        new_id_mapping[(a, b)] = particle_id
                        new_p0.append(new)

                        # Store trajectory in a deque with a fixed maxlen
                        if particle_id not in trajectories:
                            trajectories[particle_id] = deque(maxlen=trajectory_length)
                        trajectories[particle_id].append((a, b))

                        # Reset lost count since we see this particle
                        lost_counts[particle_id] = 0

                        # Draw the trajectory lines
                        pts = list(trajectories[particle_id][-trajectory_length:])
                        for k in range(1, len(pts)):
                            pt1 = pts[k - 1]
                            pt2 = pts[k]
                            cv2.line(mask, (int(pt1[0]), int(pt1[1])),
                                     (int(pt2[0]), int(pt2[1])), (0, 255, 0), 1)

            p0 = np.array(new_p0).reshape(-1, 1, 2) if new_p0 else None
            id_mapping = new_id_mapping

        # Detect new particles periodically and assign unique IDs
        if frame_count % 10 == 0 or p0 is None:
            kernel = np.ones((5, 5), np.uint8)  # Define the structuring element
            tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
            _, binary = cv2.threshold(tophat, 100, 255, cv2.THRESH_BINARY)

            new_features = cv2.goodFeaturesToTrack(binary, mask=None, **feature_params)

            if new_features is not None:
                for new in new_features:
                    a, b = new.ravel()

                    # Assign a new ID only if the particle is not already tracked
                    if (a, b) not in id_mapping:
                        particle_id = next_particle_id
                        next_particle_id += 1

                        trajectories[particle_id] = [(a, b)]
                        id_mapping[(a, b)] = particle_id

                        if p0 is not None:
                            p0 = np.vstack((p0, new.reshape(-1, 1, 2)))
                        else:
                            p0 = new.reshape(-1, 1, 2)

        for pid in list(lost_counts.keys()):

            if lost_counts[pid] > 50:
                # This particle is lost for too long, remove from local dicts
                if pid in trajectories:
                    del trajectories[pid]

                # We remove it from 'id_mapping' by removing all occurrences
                # This is a bit brute force, but ensures we get rid of
                # that pid's old positions
                to_remove = []
                for (x, y), stored_pid in id_mapping.items():
                    if stored_pid == pid:
                        to_remove.append((x, y))
                for point in to_remove:
                    del id_mapping[point]

                # For safety, remove from lost_counts
                del lost_counts[pid]

        frame_count += 1
        multiprocessing_queue.put((frame, [(pid, trajectories[pid][-1]) for pid in trajectories if len(trajectories[pid]) > 0]))
        combined = cv2.add(frame, mask)

        cv2.imshow('Particle Trajectories', combined)

        cv2.waitKey(1)
        old_gray = gray.copy()


# Multiprocessing Worker Pool
def worker_process(multiprocessing_queue, shared_dict, data_queue, dict_lock,
                   shutdown_event):
    while not shutdown_event.is_set():
        try:
            # Use a small timeout so we can periodically check shutdown_event.
            frame, particle_positions = multiprocessing_queue.get(timeout=0.1)
        except queue.Empty:
            # If no data is available and we're shutting down, exit.
            if shutdown_event.is_set():
                break
            else:
                continue

        results = []
        for pid, pos in particle_positions:
            size = np.random.uniform(10, 20)  # Dummy size calculation
            velocity = np.random.uniform(0, 5)  # Dummy velocity calculation

            with dict_lock:
                shared_dict[pid] = {'size': size, 'velocity': velocity, 'position': pos}
            results.append([pid, size, velocity, pos])

        # Send results on to CSV
        data_queue.put(results)

# CSV Writing Thread
def write_csv(data_queue, shutdown_event, csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'Particle ID', 'Size', 'Velocity', 'Position'])
        while not shutdown_event.is_set():
            try:
                results = data_queue.get(timeout=0.1)
            except queue.Empty:
                # If no data is available and we're shutting down, exit.
                if shutdown_event.is_set():
                    break
                else:
                    continue
            for result in results:
                current_time = datetime.datetime.now().strftime('%H:%M:%S.%f')
                writer.writerow([current_time] + result)

def graph_process(shared_dict, dict_lock, shutdown_event):
    """Run the PyQtGraph visualization in its own process"""
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtCore, QtWidgets

    # Create a QApplication in this process
    app = QtWidgets.QApplication([])

    # Create window with graphs
    win = pg.GraphicsLayoutWidget(title="Real-Time Size and Velocity")
    win.resize(800, 600)

    # Create plots
    size_plot = win.addPlot(title="Particle Sizes")
    size_plot.setLabel('left', 'Size')
    size_plot.setLabel('bottom', 'Particle ID')
    size_plot.enableAutoRange(x=False, y=True)
    size_scatter = size_plot.plot(pen=None, symbol='o', symbolBrush=(255, 0, 0))

    win.nextRow()

    vel_plot = win.addPlot(title="Particle Velocities")
    vel_plot.setLabel('left', 'Velocity')
    vel_plot.setLabel('bottom', 'Particle ID')
    vel_plot.enableAutoRange(x=False, y=True)
    vel_scatter = vel_plot.plot(pen=None, symbol='x', symbolBrush=(0, 255, 0))

    max_points = 50

    # Define update function within this process
    def update_plots():
        with dict_lock:
            # Make a copy to avoid long lock times
            local_dict = {pid: data.copy() for pid, data in shared_dict.items()}

        if not local_dict:  # Skip if empty
            return

        # Sort by particle ID so we can control how they appear on the x-axis
        sorted_pids = sorted(local_dict.keys())
        # Keep only the last 50 IDs
        if len(sorted_pids) > max_points:
            # The "newest" 50 are the last 50 in sorted order
            keep_pids = sorted_pids[-max_points:]
            old_pids = sorted_pids[:-max_points]
        else:
            keep_pids = sorted_pids
            old_pids = []

        ids = []
        sizes = []
        velocities = []

        for pid in keep_pids:
            data = local_dict[pid]
            if 'size' in data and 'velocity' in data:
                ids.append(pid)
                sizes.append(data['size'])
                velocities.append(data['velocity'])

        if ids:  # Only update if we have data
            size_scatter.setData(ids, sizes)
            vel_scatter.setData(ids, velocities)
            size_plot.setXRange(ids[0], ids[-1], padding=0.01)
            vel_plot.setXRange(ids[0], ids[-1], padding=0.01)

        if old_pids:
            with dict_lock:
                for pid in old_pids:
                    shared_dict.pop(pid, None)  # Safely remove if present

    # Set up timer for plot updates
    timer = QtCore.QTimer()
    timer.timeout.connect(update_plots)
    timer.start(200)  # Update every 200ms

    # Handle window close events
    def handle_close_event(event):
        shutdown_event.set()
        event.accept()

    win.closeEvent = handle_close_event

    # Additional timer to check for shutdown signal
    def check_shutdown():
        if shutdown_event.is_set():
            app.quit()

    shutdown_timer = QtCore.QTimer()
    shutdown_timer.timeout.connect(check_shutdown)
    shutdown_timer.start(100)

    # Show the window and start the event loop
    win.show()
    app.exec_()
    print("Graph process terminating")

# Main execution
if __name__ == '__main__':
    # Video Capture Setup
    cap = cv2.VideoCapture("../Test Data/Videos/MicrosphereVideo3_10Min.mp4")

    # CSV Setup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"particle_data_{timestamp}.csv"

    # Initialize Queues
    frame_queue = queue.Queue(maxsize=500)
    multiprocessing_queue = mp.Queue()
    data_queue = mp.Queue()

    shared_dict = mp.Manager().dict()

    # Create a lock
    dict_lock = mp.Lock()
    shutdown_event = mp.Event()

    graph_proc = mp.Process(
        target=graph_process,
        args=(shared_dict, dict_lock, shutdown_event),
        daemon=True
    )
    graph_proc.start()

    ############### Threads and Processes ##############
    # Thread for acquiring frames
    acquire_thread = threading.Thread(target=acquire_frames, args=(cap, frame_queue, shutdown_event), daemon=True)
    acquire_thread.start()

    # Thread for particle tracking
    particle_thread = threading.Thread(target=particle_tracking, args=(frame_queue, multiprocessing_queue,shared_dict, dict_lock, shutdown_event), daemon=True)
    particle_thread.start()

    # Worker processes
    workers = [mp.Process(target=worker_process, args=(multiprocessing_queue, shared_dict, data_queue, dict_lock,shutdown_event), daemon=True)
               for _ in range(mp.cpu_count() - 1)]
    for w in workers:
        w.start()

    # CSV-writing thread
    csv_thread = threading.Thread(target=write_csv, args=(data_queue, shutdown_event, csv_filename), daemon=False)
    csv_thread.start()

    csv_thread.join()
    for w in workers:
        w.join()

    cap.release()
    cv2.destroyAllWindows()
