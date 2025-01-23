import cv2


def main():
    # Attempt to open the ThorCam using OpenCV
    # The camera index may be 0 (first camera). Try increasing it (e.g., 1, 2) if it doesn't work.
    camera_index = 0
    capture = cv2.VideoCapture(camera_index)

    # Check if the camera has been successfully opened
    if not capture.isOpened():
        print("Error: Could not open the ThorCam. Is it connected?")
        return

    print("Success: ThorCam opened. Press 'q' to exit.")

    # Display the live video feed
    while True:
        # Read a frame from the camera
        ret, frame = capture.read()
        if not ret:
            print("Error: Could not read frame from the ThorCam. Exiting.")
            break

        # Display the video feed in a window
        cv2.imshow("ThorCam Live View", frame)

        # Press 'q' key to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources and close the live view window
    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
