import cv2
import numpy as np
from config import CAMERA_INDEX, PROFILE_DIR, WARP_WIDTH, WARP_HEIGHT
from utils.vision import select_corners, compute_homography, warp_image

def main():
    print("[INFO] Starting camera...")
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        raise RuntimeError(f"[ERROR] Cannot open camera at index {CAMERA_INDEX}")

    print("[INFO] Press 's' to select arena corners when ready.")
    frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Failed to grab frame.")
            continue

        # Show live preview
        cv2.imshow("Live Camera Feed - Press 's' to select corners", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            print("[INFO] Selection triggered.")
            break
        elif key == ord('q'):
            print("[INFO] Exiting without saving.")
            cap.release()
            cv2.destroyAllWindows()
            return

    # Select corners on the latest frame
    corners = select_corners(frame)

    # Compute homography
    matrix = compute_homography(corners, WARP_WIDTH, WARP_HEIGHT)

    # Warp and preview the result
    warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
    cv2.imshow("Warped Arena Preview", warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Save matrix
    label = input("Enter lighting scenario label (e.g. bright, dark, dim): ").strip().lower()
    save_path = PROFILE_DIR / f"{label}_matrix.npy"
    np.save(save_path, matrix)
    print(f"[INFO] Matrix saved to: {save_path}")

    cap.release()

if __name__ == "__main__":
    main()