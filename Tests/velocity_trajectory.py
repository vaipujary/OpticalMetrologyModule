import cProfile
import pstats
import io
import sys
import cv2
import time
from VideoProcessor import VideoProcessor

def main():
    # Path to the video file to test
    video_path = "../Test Data/Videos/MicrosphereVideo3.avi"  # Replace with the actual path to your video file

    # Initialize VideoProcessor
    video_processor = VideoProcessor(ui_video_label=None, input_mode="file", video_source=video_path, save_data_enabled=False)

    # Test if tracking can be initialized
    if not video_processor.initialize_tracking():
        print("Failed to initialize video processor.")
        sys.exit(1)

    # Create a window to display the video
    cv2.namedWindow("Velocities and Trajectories", cv2.WINDOW_NORMAL)
    pr = cProfile.Profile()  # Create a profile object
    pr.enable()  # Start profiling
    frame_count = 0  # Initialize frame counter
    max_frames = 500  # Number of frames to profile. Adjust as needed
    print(f"FPS: {video_processor.fps}")

    start_time = time.time()
    while frame_count < max_frames:
        # Process the next frame
        processed_frame = video_processor.track_particles(save_data_enabled=False)

        if processed_frame is None:
            print("End of video or an error occurred.")
            break

        # Display the processed frame
        cv2.imshow("Velocities and Trajectories", processed_frame)

        # Press 'q' to quit the testing loop
        if cv2.waitKey(int(1000/video_processor.fps)) & 0xFF == ord('q'):
            break
        frame_count += 1  # increment frame counter

    end_time = time.time()
    pr.disable()  # Stop profiling
    s = io.StringIO()  # Use StringIO to capture output
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')  # Sort by cumulative time
    ps.print_stats()  # Print statistics to the StringIO object
    print(s.getvalue())  # Print output

    print("Elapsed time: {:.2f} seconds".format(end_time - start_time))
    # Release resources and close the window
    video_processor.camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

# TEST FOR OPENCV VIDEO PLAYBACK SPEED
# def main():
#     video_path = "../Test Data/Videos/MicrosphereVideo3.avi"
#
#     cap = cv2.VideoCapture(video_path)  # Use cv2.VideoCapture directly
#
#     if not cap.isOpened():
#         print("Error opening video file.")
#         sys.exit(1)
#
#     cv2.namedWindow("Video Player", cv2.WINDOW_NORMAL)
#
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     start_time = time.time()
#     while True:
#         ret, frame = cap.read()
#
#         if not ret:  # Check if a frame was successfully read
#             print("End of video or an error occurred.")
#             break
#
#         cv2.imshow("Video Player", frame)
#
#         if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
#             break
#     end_time = time.time()
#     print("Elapsed time: {:.2f} seconds".format(end_time - start_time))
#     cap.release()  # Release the VideoCapture object
#     cv2.destroyAllWindows()