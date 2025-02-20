import sys
import cv2
import time
import datetime
from VideoProcessor import VideoProcessor
from OpticalMetrologyModule import OpticalMetrologyModule


def main():
    # Path to the video file to test
    video_path = "../Test Data/Videos/MicrosphereVideo3.avi"  # Replace with the actual path to your video file

    # Create a timestamped filename for the CSV output
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = f"particle_data_{timestamp}.csv"  # CSV file name

    # Initialize VideoProcessor
    video_processor = VideoProcessor(ui_video_label=None, input_mode="file", video_source=video_path, save_data_enabled=True)
    optical_metrology_module = OpticalMetrologyModule(debug=False, output_csv=output_csv,
                                                      fps=video_processor.fps)

    # Test if tracking can be initialized
    if not video_processor.initialize_tracking():
        print("Failed to initialize video processor.")
        sys.exit(1)

    # Create a window to display the video
    cv2.namedWindow("Optical Metrology Module", cv2.WINDOW_NORMAL)

    optical_metrology_module.initialize_csv()

    while True:
        start_time = time.time()  # Start time for frame processing
        # Process the next frame
        processed_frame = video_processor.process_frame(save_data_enabled=True)
        end_time = time.time()  # End time for frame processing
        processing_time = end_time - start_time

        if processed_frame is None:
            print("End of video or an error occurred.")
            break

        # Display the processed frame
        cv2.imshow("Optical Metrology Module", processed_frame)

        # Press 'q' to quit the testing loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources and close the window
    video_processor.camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()