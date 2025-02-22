import multiprocessing as mp
import threading
import queue
import cv2
import time
import csv
import numpy as np
import os
from VideoProcessor import VideoProcessor
from OpticalMetrologyModule import OpticalMetrologyModule


def run_multiprocessing(input_queue, output_array, lock, event, video_path, output_csv_path):
    video_processor_local = VideoProcessor(ui_video_label=None, input_mode="file", video_source=video_path,
                                           save_data_enabled=True)
    video_processor_local.initialize_tracking()

    video_processor_local.optical_metrology_module = OpticalMetrologyModule(parent_ui=None,
                                                                            debug=False)

    while True:
        frame_data = input_queue.get()
        if frame_data is None:
            # input_queue.task_done()  # Indicate that a formerly enqueued task is complete
            break

        frame_number, frame = frame_data
        output, frame_gray, new_p0, new_trajectories, new_particle_colors, new_id_mapping, updated_mask = video_processor_local.track_particles(
            frame)

        results = video_processor_local.optical_metrology_module.perform_metrology_calculations(output,
                                                                                                new_trajectories,
                                                                                                video_processor_local.scaling_factor)
        if results:
            for result in results:
                video_processor_local.optical_metrology_module.log_to_csv(**result,
                                                                          save_data_enabled=video_processor_local.save_data_enabled)  # Log data as it's processed

        with lock:  # Acquire lock before writing to shared array
            output_array[frame_number] = output.copy()

        # mask_queue.put(updated_mask.copy())  # Put a copy of the mask into the queue

        event.set()  # Signal that processing is complete for this frame

        video_processor_local.old_gray = frame_gray
        video_processor_local.p0 = new_p0
        video_processor_local.trajectories = new_trajectories
        video_processor_local.particle_colors = new_particle_colors
        video_processor_local.id_mapping = new_id_mapping


def video_processing_thread(input_queue, video_path, num_processes):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for frame_number in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        input_queue.put((frame_number, frame.copy()))

    cap.release()
    for _ in range(num_processes):  # Send termination signals
        input_queue.put(None)


def display_thread(output_array, lock, event, frame_count):
    for frame_number in range(frame_count):
        event.wait()  # Wait for frame to be processed
        event.clear()
        # mask = mask_queue.get(timeout=1)  # Get the latest mask from the queue
        # mask = mask.astype(np.uint8)
        #
        # if mask is None:
        #     print("Mask queue timeout!")
        #     continue  # Skip this frame if mask isn't available

        with lock:
            output = output_array[frame_number]
        if output is not None and output.size > 0:  # Check if the output is valid and not empty
            # output = cv2.add(output, mask)
            # cv2.imshow("Mask", mask)

            cv2.imshow("Processed Frame", output)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

def main():
    # Ensuring output path exists
    output_csv_path = os.path.abspath("particle_data.csv")  # Or get it from config
    output_csv_dir = os.path.dirname(output_csv_path)  # Extract the directory from the path

    if not os.path.exists(output_csv_dir):
        os.makedirs(output_csv_dir)  # Creates missing directory/directories in the path

    video_path = "../Test Data/Videos/MicrosphereVideo3.avi"

    num_processes = mp.cpu_count() - 1  # Use most CPU cores but leave one for other tasks

    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()  # Read the first frame to get dimensions
    if not ret:
        print("Error reading video file.")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()  # Release the capture immediately

    with mp.Manager() as manager:
        # mask_queue = manager.Queue(maxsize=1)
        input_queue = manager.JoinableQueue()  # Queue to hold a few frames for processing
        output_array = manager.list([None] * frame_count)  # manager for shared state
        lock = manager.Lock()
        event = manager.Event()

        calculation_processes = [mp.Process(target=run_multiprocessing,
                                            args=(input_queue, output_array, lock, event, video_path, output_csv_path)) for _ in range(num_processes)]

        for p in calculation_processes:
            p.start()

        video_thread = threading.Thread(target=video_processing_thread,
                                        args=(input_queue, video_path, num_processes))

        display_thread_instance = threading.Thread(target=display_thread, args=(output_array, lock, event, frame_count))

        video_thread.start()
        print("after video_thread.start()")
        display_thread_instance.start()
        print("after display_thread_instance.start()")
        video_thread.join()  # Wait for the video processing thread to finish.
        print("after video_thread.join()")

        for p in calculation_processes:
            p.join()

        display_thread_instance.join()
        print("after display_thread_instance.join()")
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

