import cv2                            # OpenCV for video capture and display
import os                             # OS module for file and directory operations
from datetime import datetime         # To generate timestamps for filenames
from config import CAMERA_INDEX       # Camera index from config file

# Directory to save captured images
SAVE_DIR = "dataset/images"
os.makedirs(SAVE_DIR, exist_ok=True)  # Create the directory if it doesn't exist

def main():
    print("[INFO] Starting camera...")

    # Open the camera (use cv2.CAP_DSHOW for Windows to avoid delay)
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("[ERROR] Cannot access camera.")
        return

    print("[INFO] Press SPACE to save frame, ESC to quit.")

    # Optional short wait for camera to stabilize
    cv2.waitKey(2000)

    frame_count = 0  # Counter for saved frames

    while True:
        ret, frame = cap.read()
        if not ret:
            continue  # Skip this iteration if frame not read

        # Show the current frame in a window
        cv2.imshow("Capture Dataset", frame)

        key = cv2.waitKey(1)

        if key == 27:  # ESC key to exit
            break
        elif key == 32:  # SPACE key to save frame
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(SAVE_DIR, f"{timestamp}.jpg")

            # Save the frame to disk
            cv2.imwrite(filename, frame)
            print(f"[SAVED] {filename}")

            # Update and print total saved count
            frame_count += 1
            print(f"[INFO] Total frames saved: {frame_count}")

    # Release camera and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Run main only if this file is executed directly
if __name__ == "__main__":
    main()
