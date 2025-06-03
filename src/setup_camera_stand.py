import cv2
import os
import numpy as np
from config import CAMERA_INDEX, PROFILE_DIR, WARP_WIDTH, WARP_HEIGHT
from utils.vision import select_corners, compute_homography, warp_image

def main():
    # ⏩ Speed boost
    os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "1"

    print("[INFO] Starting camera...")
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

    if not cap.isOpened():
        raise RuntimeError(f"[ERROR] Cannot open camera at index {CAMERA_INDEX}")

    print("[INFO] Press 's' to select arena corners when ready.")
    frame = None

    # Create a standard resizable window instead of fullscreen
    window_name = "Live Camera Feed - Press 's' to select corners"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Failed to grab frame.")
            continue

        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            print("[INFO] Selection triggered.")
            break
        elif key == ord('q'):
            print("[INFO] Exiting without saving.")
            cap.release()
            cv2.destroyAllWindows()
            return

    corners = select_corners(frame)

    matrix = compute_homography(corners, WARP_WIDTH, WARP_HEIGHT)

    warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)

    # Show the warped image in a standard window
    warp_window = "Warped Arena Preview"
    cv2.namedWindow(warp_window, cv2.WINDOW_NORMAL)
    cv2.imshow(warp_window, warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    label = input("Enter lighting scenario label (e.g. bright, dark, dim): ").strip().lower()
    save_path = PROFILE_DIR / f"{label}_matrix.npy"
    np.save(save_path, matrix)
    print(f"[INFO] Matrix saved to: {save_path}")

    cap.release()

if __name__ == "__main__":
    main()
