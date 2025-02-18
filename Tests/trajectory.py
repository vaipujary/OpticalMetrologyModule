import sys
import cv2
from VideoProcessor import VideoProcessor


def main():
    # Path to the video file to test
    video_path = "../Test Data/Videos/MicrosphereVideo3.avi"  # Replace with the actual path to your video file

    # Initialize VideoProcessor
    video_processor = VideoProcessor(ui_video_label=None, input_mode="file", video_source=video_path)

    # Test if tracking can be initialized
    if not video_processor.initialize_tracking():
        print("Failed to initialize video processor.")
        sys.exit(1)

    # Create a window to display the video
    cv2.namedWindow("Trajectories", cv2.WINDOW_NORMAL)

    while True:
        # Process the next frame
        processed_frame = video_processor.process_frame()

        if processed_frame is None:
            print("End of video or an error occurred.")
            break

        # Display the processed frame
        cv2.imshow("Trajectories", processed_frame)

        # Press 'q' to quit the testing loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources and close the window
    video_processor.camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()