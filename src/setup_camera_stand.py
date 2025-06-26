import cv2
import os
import numpy as np
from config import CAMERA_INDEX, PROFILE_DIR, WARP_WIDTH, WARP_HEIGHT
from utils.vision import select_corners, compute_homography, warp_image

def sort_polygon_points(points):
    """Sort points clockwise around center (robust polygon sort)"""
    points = np.array(points)
    center = np.mean(points, axis=0)
    angles = np.arctan2(points[:,1] - center[1], points[:,0] - center[0])
    sorted_points = points[np.argsort(angles)]
    return sorted_points

def main():
    os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "1"

    print("[INFO] Starting camera...")
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

    if not cap.isOpened():
        raise RuntimeError(f"[ERROR] Cannot open camera at index {CAMERA_INDEX}")

    print("[INFO] Press 's' to select arena corners.")
    window_name = "Live Camera Feed"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Failed to grab frame.")
            continue

        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            print("[INFO] Selecting corners...")
            break
        elif key == ord('q'):
            print("[INFO] Exiting without saving.")
            cap.release()
            cv2.destroyAllWindows()
            return

    corners = select_corners(frame)
    matrix = compute_homography(corners, WARP_WIDTH, WARP_HEIGHT)
    warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)

    # Warp preview
    cv2.imshow("Warped Arena", warped)
    cv2.waitKey(500)

    # === Kryds markering ===
    print("[INFO] Click 4 corners around the CROSS (egg obstacle)...")
    clone = frame.copy()
    cross_points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(cross_points) < 4:
            print(f"[INFO] Point {len(cross_points)+1}: ({x}, {y})")
            cross_points.append([x, y])
            cv2.circle(clone, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Click CROSS", clone)

    cv2.imshow("Click CROSS", clone)
    cv2.setMouseCallback("Click CROSS", click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(cross_points) != 4:
        print("[ERROR] You must click exactly 4 points for the CROSS")
        return

    # Automatisk sortering af punkter
    sorted_cross = sort_polygon_points(cross_points)

    # Konverter til arena-koordinater
    cross_pts = np.array([sorted_cross], dtype='float32')  # (1, 4, 2)
    cross_pts_arena = cv2.perspectiveTransform(cross_pts, matrix)[0]  # (4, 2)

    label = input("Enter lighting label (e.g. bright): ").strip().lower()
    matrix_path = PROFILE_DIR / f"{label}_matrix.npy"
    cross_path = PROFILE_DIR / f"{label}_cross.npy"

    np.save(matrix_path, matrix)
    np.save(cross_path, cross_pts_arena)
    print(f"[INFO] Matrix saved to: {matrix_path}")
    print(f"[INFO] Cross polygon saved to: {cross_path} (arena coords)")

    cap.release()

if __name__ == "__main__":
    main()
