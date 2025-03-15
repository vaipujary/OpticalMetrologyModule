import cv2
import multiprocessing as mp
import threading
import queue
import csv
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import datetime


# Function for acquiring frames
def acquire_frames(cap, frame_queue, display_queue, shutdown_event):
    frame_id = 0

    while cap.isOpened() and not shutdown_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        try:
            while display_queue.full():
                display_queue.get_nowait()
            display_queue.put(frame, block=False)

            frame_queue.put(frame, block=False)

        except queue.Full:
            pass

        frame_id += 1

    shutdown_event.set() # Signal other processes/threads to stop

# Particle Tracking Thread
def particle_tracking(frame_queue, multiprocessing_queue, shutdown_event):

    try:
        # Get the initial frame from the queue (blocks until available or shutdown_event is set)
        old_frame = frame_queue.get(timeout=2)
    except queue.Empty:
        # If we can't get a frame in time, or if shutting down, exit
        return

    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

    # Parameters for Lucas-Kanade Optical Flow
    lk_params = dict(winSize=(20, 20),
                     maxLevel=4,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.03))

    # Parameters for goodFeaturesToTrack
    feature_params = dict(maxCorners=5,
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

    while not shutdown_event.is_set():

        frame = frame_queue.get()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = np.zeros_like(frame)
        new_p0 = []
        new_id_mapping = {}

        if p0 is not None:
            p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, gray, p0, None, **lk_params)

            if p1 is not None:
                for i, (new, old) in enumerate(zip(p1, p0)):
                    a, b = new.ravel()
                    c, d = old.ravel()

                    if (c, d) in id_mapping:
                        pid = id_mapping[(c, d)]
                        new_id_mapping[(a, b)] = pid

                    # Retrieve or assign a particle ID
                    particle_id = id_mapping.get(tuple(old.ravel()))
                    if particle_id is not None and st[i, 0] == 1:
                        new_id_mapping[(a, b)] = particle_id  # Update ID mapping
                        new_p0.append(new)  # Keep point for next frame

                        # Store trajectory
                        if particle_id in trajectories:
                            trajectories[particle_id].append((a, b))
                        else:
                            trajectories[particle_id] = [(a, b)]

                        # Limit trajectory history length
                        trajectories[particle_id] = trajectories[particle_id][-trajectory_length:]

                        for k in range(1, len(trajectories[particle_id])):
                            pt1 = trajectories[particle_id][k - 1]
                            pt2 = trajectories[particle_id][k]
                            cv2.line(mask, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])), (0, 255, 0), 1)

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
        writer.writerow(['Particle ID', 'Size', 'Velocity', 'Position'])
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
                writer.writerow(result)


# # Trajectory Display Thread
# def display_trajectories(display_queue, shared_dict, dict_lock, shutdown_event, trajectory_length=30):
#
#     frame_count = 0
#     trajectories = {}
#     colors = {}
#
#     while not shutdown_event.is_set():
#         try:
#             frame = display_queue.get(timeout=0.1)
#         except queue.Empty:
#             # If no data is available and we're shutting down, exit.
#             if shutdown_event.is_set():
#                 break
#             else:
#                 continue
#
#         mask = np.zeros_like(frame)
#
#         with dict_lock:
#             # Iterate over all trajectories in the shared dictionary
#             for particle_id, data in shared_dict.items():
#                 # if particle_id not in colors:
#                 #     colors[particle_id] = tuple(np.random.randint(0, 255, 3).tolist())
#
#                 if particle_id not in trajectories:
#                     trajectories[particle_id] = []
#
#                 trajectories[particle_id].append(data['position'])
#                 trajectories[particle_id] = trajectories[particle_id][
#                                             -trajectory_length:]  # Limit trajectory history length
#
#                 recent_trajectory = trajectories[particle_id]
#
#                 for k in range(1, len(recent_trajectory)):
#                     pt1 = recent_trajectory[k - 1]
#                     pt2 = recent_trajectory[k]
#                     cv2.line(mask, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])), (0, 255, 0), 2)
#
#         combined = cv2.add(frame, mask)
#
#         cv2.imshow('Particle Trajectories', combined)
#
#         cv2.waitKey(1)
#
#         frame_count += 1

# Real-time Graph Update Thread
def graph_update(shared_dict, shutdown_event):
    app = QtGui.QGuiApplication([])
    win = pg.GraphicsLayoutWidget(title="Real-Time Size and Velocity")
    win.resize(600, 400)

    size_plot = win.addPlot(title="Particle Sizes")
    size_scatter = size_plot.plot(pen=None, symbol='o')

    win.nextRow()

    vel_plot = win.addPlot(title="Particle Velocities")
    vel_scatter = vel_plot.plot(pen=None, symbol='x')

    def update():
        sizes, velocities = [], []
        ids = []
        for pid, data in shared_dict.items():
            ids.append(pid)
            sizes.append(data['size'])
            velocities.append(data['velocity'])
        size_scatter.setData(ids, sizes)
        vel_scatter.setData(ids, velocities)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(200)

    # This timer checks if the main program wants us to shut down
    def check_for_shutdown():
        if shutdown_event.is_set():
            QtGui.QApplication.quit()

    shutdown_timer = QtCore.QTimer()
    shutdown_timer.timeout.connect(check_for_shutdown)
    shutdown_timer.start(100)  # Check every 100 ms

    win.show()
    QtGui.QApplication.instance().exec_()

# Main execution
if __name__ == '__main__':
    # Video Capture Setup
    cap = cv2.VideoCapture("../Test Data/Videos/MicrosphereVideo3_10Min.mp4")

    # CSV Setup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"particle_data_{timestamp}.csv"

    # Initialize Queues
    frame_queue = queue.Queue(maxsize=100)
    multiprocessing_queue = mp.Queue()
    data_queue = mp.Queue()
    display_queue = queue.Queue(maxsize=100)

    shared_dict = mp.Manager().dict()

    # Create a lock
    dict_lock = mp.Lock()
    shutdown_event = mp.Event()

    # Threads and Processes
    # Thread for acquiring frames
    acquire_thread = threading.Thread(target=acquire_frames, args=(cap, frame_queue, display_queue, shutdown_event), daemon=True)
    acquire_thread.start()

    # Thread for particle tracking
    particle_thread = threading.Thread(target=particle_tracking, args=(frame_queue, multiprocessing_queue,shutdown_event), daemon=True)
    particle_thread.start()

    # Worker processes
    workers = [mp.Process(target=worker_process, args=(multiprocessing_queue, shared_dict, data_queue, dict_lock,shutdown_event), daemon=True)
               for _ in range(mp.cpu_count() - 1)]
    for w in workers:
        w.start()

    # CSV-writing thread
    csv_thread = threading.Thread(target=write_csv, args=(data_queue, shutdown_event, csv_filename), daemon=False)
    csv_thread.start()

    # # Thread for displaying trajectories
    # display_thread = threading.Thread(target=display_trajectories, args=(display_queue, shared_dict, dict_lock, shutdown_event), daemon=True)
    # display_thread.start()

    # # Thread for real-time graph updates
    # graph_thread = threading.Thread(target=graph_update, args=(shared_dict, shutdown_event), daemon=True)
    # graph_thread.start()

    csv_thread.join()

    cap.release()
    cv2.destroyAllWindows()
