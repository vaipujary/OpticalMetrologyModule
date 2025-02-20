import cv2
import datetime
import os
import pandas as pd
from VideoProcessor import VideoProcessor
from OpticalMetrologyModule import OpticalMetrologyModule


def test_csv_output():
    # Path to the test video file (replace with your test video)
    video_path = "../Test Data/Videos/MicrosphereVideo3.avi"

    # Create a temporary CSV file for testing
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = f"test_particle_data_{timestamp}.csv"

    # Print the full path of the output CSV file
    print(f"CSV file path: {os.path.abspath(output_csv)}")

    # Initialize VideoProcessor and OpticalMetrologyModule
    video_processor = VideoProcessor(ui_video_label=None, input_mode="file", video_source=video_path,
                                     save_data_enabled=True)
    optical_metrology_module = OpticalMetrologyModule(debug=False, output_csv=output_csv,
                                                      fps=video_processor.fps)

    try:
        # Initialize tracking and CSV file
        if not video_processor.initialize_tracking():
            print("Failed to initialize video processor.")
            return False  # Indicate test failure

        optical_metrology_module.initialize_csv()

        # Process a few frames (adjust the number as needed)
        num_frames_to_process = 10
        # Get the actual number of frames
        actual_frame_count = int(video_processor.camera.get(cv2.CAP_PROP_FRAME_COUNT))
        num_frames_to_process = min(num_frames_to_process, actual_frame_count)

        for _ in range(num_frames_to_process):
            processed_frame = video_processor.process_frame(save_data_enabled=True)
            if processed_frame is None:
                print("End of video or error occurred prematurely.")
                return False

        # Verify CSV file contents
        # Check if the file exists and has data
        if not os.path.exists(output_csv):
            print(f"CSV file not found: {output_csv}")
            return False

        try:
            df = pd.read_csv(output_csv)  # Use pandas to easily work with CSV data
            # Add checks relevant to your application, for example:
            if df.empty:
                print("CSV file is empty.")
                return False

            # expected_frame_numbers = set(range(num_frames_to_process))  # expected numbers, assuming 0-indexed frames
            # frame_numbers_in_csv = set(df['Frame'])  # Set for efficient comparison
            #
            # if frame_numbers_in_csv != expected_frame_numbers:  # Checks if expected numbers are present in CSV
            #     missing_frames = expected_frame_numbers - frame_numbers_in_csv
            #     extra_frames = frame_numbers_in_csv - expected_frame_numbers
            #     if missing_frames:
            #         print(f"Missing data for frames: {', '.join(map(str, sorted(missing_frames)))}")
            #     if extra_frames:
            #         print(f"Unexpected extra data for frames: {', '.join(map(str, sorted(extra_frames)))}")
            #     return False

            # Check for NaN values
            if df.isnull().values.any():
                print("CSV file contains NaN values.")
                return False

            # Example: Check existence of expected columns
            expected_columns = ["Frame", "Timestamp (s)", "Particle ID", "X (mm)", "Y (mm)", "Size (um)",
                            "Velocity (mm/s)", "Trajectory (mm)"]

            if not all(col in df.columns for col in expected_columns):
                print("CSV file is missing expected columns.")
                missing_cols = set(expected_columns) - set(df.columns)
                print(f"Missing columns: {missing_cols}")
                return False

        except pd.errors.EmptyDataError:  # Handle empty CSV edge case
            print("CSV file is empty.")
            return False
        except pd.errors.ParserError:  # Catch other potential errors when reading the CSV
            print("CSV file is corrupted")
            return False
        except (pd.errors.EmptyDataError, pd.errors.ParserError, IOError) as e:  # Broader exception handling
            print(f"Error reading or parsing CSV: {e}")  # More informative error message
            return False
        return True  # Indicate test success
    except Exception as e:  # Catch any unexpected exceptions in other parts of the test function
        print(f"An unexpected error occurred: {e}")
        return False

    finally:
        # Clean up: Release resources, close windows, delete the temporary file
        video_processor.camera.release()
        cv2.destroyAllWindows()
        os.remove(output_csv)


if __name__ == "__main__":
    if test_csv_output():
        print("CSV output test passed.")
    else:
        print("CSV output test failed.")
