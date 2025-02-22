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


def run_multiprocessing(input_queue, output_queue, video_path):
    video_processor_local = VideoProcessor(ui_video_label=None, input_mode="file", video_source=video_path,
                                           save_data_enabled=True)
    video_processor_local.initialize_tracking()

    video_processor_local.optical_metrology_module = OpticalMetrologyModule(parent_ui=None,
                                                                            debug=False)

    while True:
        frame_data = input_queue.get()
        if frame_data is None:
            input_queue.task_done()  # Indicate that a formerly enqueued task is complete
            break

        frame_number, frame = frame_data
        output, frame_gray, new_p0, new_trajectories, new_particle_colors, new_id_mapping = video_processor_local.track_particles(
            frame)

        results = video_processor_local.optical_metrology_module.perform_metrology_calculations(output,
                                                                                                new_trajectories,
                                                                                                video_processor_local.scaling_factor)
        if results:
            for result in results:
                video_processor_local.optical_metrology_module.log_to_csv(**result,
                                                                          save_data_enabled=video_processor_local.save_data_enabled)  # Log data as it's processed

        video_processor_local.old_gray = frame_gray
        video_processor_local.p0 = new_p0
        video_processor_local.trajectories = new_trajectories
        video_processor_local.particle_colors = new_particle_colors
        video_processor_local.id_mapping = new_id_mapping

        output_queue.put((frame_number, output))
        input_queue.task_done()


def video_processing_thread(input_queue, output_queue, video_path, num_processes, display_queue):

    video_processor_local = VideoProcessor(ui_video_label=None, input_mode="file", video_source=video_path,
                                           save_data_enabled=True)

    video_processor_local.initialize_tracking()

    frame_count = 0

    cap = cv2.VideoCapture(video_path)

    while True: # Main loop for processing frames
        ret, frame = cap.read()
        if not ret:
            break

        input_queue.put((frame_count, frame.copy()))
        frame_count += 1

    cap.release()

    for _ in range(num_processes):
        input_queue.put(None)  # Signal processes to stop

    for _ in range(frame_count):  # Retrieve all processed frames
        _, output = output_queue.get()
        display_queue.put((output, _))

    display_queue.put(None)  # Sentinel to signal end of video


def display_thread(display_queue):  # New thread for displaying results
    while True:
        item = display_queue.get()
        if item is None:
            break
        output, frame_number = item

        cv2.imshow("Processed Frame", output)  # Displaying results in order.
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit gracefully if 'q' is pressed
            break  # Exit gracefully if 'q' is pressed.
    cv2.destroyAllWindows()


def main():
    # Ensuring output path exists
    output_csv_path = os.path.abspath("particle_data.csv")  # Or get it from config
    output_csv_dir = os.path.dirname(output_csv_path)  # Extract the directory from the path

    if not os.path.exists(output_csv_dir):
        os.makedirs(output_csv_dir)  # Creates missing directory/directories in the path

    video_path = "../Test Data/Videos/MicrosphereVideo3.avi"

    input_queue = mp.JoinableQueue()  # Queue to hold a few frames for processing
    display_queue = mp.Queue()
    output_queue = mp.Queue()

    num_processes = mp.cpu_count() - 1  # Use most CPU cores but leave one for other tasks

    calculation_processes = [mp.Process(target=run_multiprocessing,
                                        args=(input_queue, output_queue, video_path)) for _ in range(num_processes)]

    for p in calculation_processes:
        p.start()

    video_thread = threading.Thread(target=video_processing_thread,
                                    args=(input_queue, output_queue, video_path, num_processes, display_queue))

    display_thread_instance = threading.Thread(target=display_thread, args=(display_queue,))

    video_thread.start()
    display_thread_instance.start()
    video_thread.join()  # Wait for the video processing thread to finish.

    for p in calculation_processes:
        p.join()

    display_thread_instance.join()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

