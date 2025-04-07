import cv2
import numpy as np
from config import CAMERA_INDEX, PROFILE_DIR, WARP_WIDTH, WARP_HEIGHT
from utils.vision import warp_image

def main():
    label = input("Enter saved scenario label (e.g. dim, bright): ").strip().lower()
    matrix_path = PROFILE_DIR / f"{label}_matrix.npy"

    if not matrix_path.exists():
        print(f"[ERROR] Matrix for scenario '{label}' not found at {matrix_path}")
        return

    print(f"[INFO] Loading matrix from: {matrix_path}")
    matrix = np.load(matrix_path)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError("[ERROR] Could not open camera")

    print("[INFO] Press 'q' to quit preview")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Failed to read frame")
            continue

        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        cv2.imshow("Warped Arena View", warped)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()