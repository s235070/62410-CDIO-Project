import cv2
import numpy as np
from config import CAMERA_INDEX, WARP_WIDTH, WARP_HEIGHT
from utils.vision import warp_image
from track.input_handler import ask_for_label, load_matrix
from track.track_arena import select_detection_zone, create_manual_mask
from track.track_balls import detect_balls_yolo, COLOR_BGR

def main():
    # 📁 Load kalibreringsmatrix
    label = ask_for_label()
    matrix = load_matrix(label)
    if matrix is None:
        return

    # 🎥 Start kamera
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Camera not accessible")
        return

    # 🔲 Udpeg manuelt detektionsområdet
    print("[INFO] Waiting for frame to define detection zone...")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        cv2.imshow("Warped Preview", warped)
        if cv2.waitKey(1) & 0xFF == ord("s"):
            print("[INFO] Selection mode triggered")
            break

    arena_polygon = select_detection_zone(warped)
    arena_mask = create_manual_mask(arena_polygon, warped.shape[:2])

    # Luk preview
    cv2.destroyWindow("Warped Preview")

    # 🔁 Hovedloop
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)

        # 🎯 Bold-detektion via YOLO
        balls = detect_balls_yolo(warped)

        # 🟢 Vis bolde i Arena View
        for label, (x, y) in balls:
            color_bgr = COLOR_BGR.get(label, (200, 200, 200))  # fallback
            cv2.circle(warped, (x, y), 10, color_bgr, 2)

        # 🔲 Tegn polygon (valgfrit)
        cv2.polylines(warped, [arena_polygon], isClosed=True, color=(180, 0, 180), thickness=2)

        # 🖼️ Vis
        cv2.imshow("Arena View", warped)
        cv2.imshow("Arena Mask", arena_mask)

        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
