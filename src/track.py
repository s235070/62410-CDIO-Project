import cv2
import numpy as np
import time
from threading import Thread
from config import CAMERA_INDEX, WARP_WIDTH, WARP_HEIGHT
from utils.vision import warp_image
from track.input_handler import ask_for_label, load_matrix
from track.track_arena import select_detection_zone, create_manual_mask
from track.track_balls import detect_balls_yolo, COLOR_BGR
from track.track_ev3 import detect_ev3
from track.track_cross import load_cross_polygon
from track.track_goal import draw_goals
from ev3_move import move_towards_ball
from ev3_control import setup_connection

# === THREAD-BASERET KAMERA ===
class VideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.stream.set(cv2.CAP_PROP_FPS, 30)
        if not self.stream.isOpened():
            print("[ERROR] Cannot open camera.")
            exit()
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            self.grabbed, self.frame = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

# === HOVEDPROGRAM ===

def main():
    setup_connection()

    label = ask_for_label().strip().lower()
    matrix = load_matrix(label)
    if matrix is None:
        return

    cross_poly = load_cross_polygon(label)
    if cross_poly is None:
        print("[WARN] No cross polygon found — robot will ignore the cross.")

    cap = VideoStream(CAMERA_INDEX).start()

    print("[INFO] Waiting for frame to define detection zone...")
    while True:
        frame = cap.read()
        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        cv2.imshow("Warped Preview", warped)
        if cv2.waitKey(1) & 0xFF == ord("s"):
            break

    arena_polygon = select_detection_zone(warped)
    arena_mask = create_manual_mask(arena_polygon, warped.shape[:2])
    cv2.destroyWindow("Warped Preview")

    while True:
        frame = cap.read()
        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        warped = draw_goals(warped)

        balls = detect_balls_yolo(warped)
        front, back, *_ = detect_ev3(warped)

        if front and back:
            center = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)
            balls = [b for b in balls if np.hypot(b[1][0] - center[0], b[1][1] - center[1]) > 60]

            if cross_poly is not None:
                dist = cv2.pointPolygonTest(np.array(cross_poly, dtype=np.float32), center, True)
                if dist >= 0 or abs(dist) < 25:
                    print(f"[CROSS] Stop tæt på kryds (dist={dist:.1f})")
                    continue

            # === Flyttet alt movement til ekstern fil ===
            move_towards_ball(front, back, balls)

        # === Visualisering ===
        for label, (x, y) in balls:
            color = COLOR_BGR.get(label, (200, 200, 200))
            cv2.circle(warped, (x, y), 10, color, 2)

        if cross_poly is not None:
            poly = np.array([cross_poly], dtype=np.int32)
            cv2.polylines(warped, [poly], True, (0, 0, 255), 2)

        if front and back:
            cv2.circle(warped, front, 8, (0, 255, 0), 2)
            cv2.circle(warped, back, 8, (255, 0, 0), 2)
            cv2.line(warped, front, back, (0, 255, 255), 2)

        cv2.polylines(warped, [arena_polygon], isClosed=True, color=(180, 0, 180), thickness=2)
        cv2.imshow("Arena View", warped)
        cv2.imshow("Arena Mask", arena_mask)

        if cv2.waitKey(1) == 27:
            break

    cap.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
