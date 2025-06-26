# Import necessary libraries
import cv2                            # OpenCV for computer vision operations
import numpy as np                   # NumPy for matrix and numerical operations
from config import CAMERA_INDEX, PROFILE_DIR, WARP_WIDTH, WARP_HEIGHT  # Configuration constants
from utils.vision import warp_image  # Custom function to apply a perspective warp

def main():
    # Prompt the user to input a lighting scenario label (e.g., "dim" or "bright")
    label = input("Enter saved scenario label (e.g. dim, bright): ").strip().lower()
    
    # Construct the path to the corresponding transformation matrix file
    matrix_path = PROFILE_DIR / f"{label}_matrix.npy"

    # Check if the matrix file exists; if not, print an error and exit
    if not matrix_path.exists():
        print(f"[ERROR] Matrix for scenario '{label}' not found at {matrix_path}")
        return

    # Load the transformation matrix from the .npy file
    print(f"[INFO] Loading matrix from: {matrix_path}")
    matrix = np.load(matrix_path)

    # Open the camera using the specified index
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError("[ERROR] Could not open camera")

    print("[INFO] Press 'q' to quit preview")

    # Continuously read frames from the camera
    while True:
        ret, frame = cap.read()  # Read a frame
        if not ret:
            print("[WARN] Failed to read frame")
            continue

        # Apply the perspective warp to the frame using the loaded matrix
        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)

        # Display the warped image in a window
        cv2.imshow("Warped Arena View", warped)

        # Break the loop and exit if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Run the main function only if this script is executed directly
if __name__ == "__main__":
    main()
