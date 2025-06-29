import cv2
import numpy as np
#imports so that they can help
import os
from config import DISABLE_MSMF
if DISABLE_MSMF:
    os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
from threading import Thread
from config import CAMERA_INDEX, WARP_WIDTH, WARP_HEIGHT
from utils.vision import warp_image
from track.input_handler import ask_for_label, load_matrix
from track.track_arena import select_detection_zone, create_manual_mask
from track.track_balls import detect_balls_yolo, COLOR_BGR
from track.track_ev3 import detect_ev3
from track.track_cross import load_cross_polygon
from track.track_goal import draw_goals
from ev3_move import move_towards_ball, stop_ev3
from ev3_control import setup_connection
from pickup_ball import pick_up_sequence
from ev3_move import move_towards_ball, stop_ev3, go_to_goal, reset_stop_state  # ← tilføj denne import


# === THREAD-BASERET KAMERA ===
class VideoStream:
    def __init__(self, src):
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
    collected_balls = 0
    MAX_BALLS = 5
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

    # Konverter polygoner til numpy arrays
    cross_poly_np = np.array(cross_poly, dtype=np.float32) if cross_poly is not None else None
    arena_np = np.array(arena_polygon, dtype=np.float32)

    def is_outside_all_polygons(point, arena, cross):
        in_arena = cv2.pointPolygonTest(arena, point, False) >= 0
        in_cross = cv2.pointPolygonTest(cross, point, False) >= 0 if cross is not None else False
        return not (in_arena or in_cross)

    # === KØR IGENNEM BILLEDER ===
    while True:
        frame = cap.read()
        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        warped, goal_a, goal_b = draw_goals(warped)

        all_balls = detect_balls_yolo(warped)
        balls = [b for b in all_balls if is_outside_all_polygons(b[1], arena_np, cross_poly_np)]

        front, back, *_ = detect_ev3(warped)

        if front and back:
            center = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)
            balls = [b for b in balls if np.hypot(b[1][0] - center[0], b[1][1] - center[1]) > 60]

            if cross_poly is not None:
                dist = cv2.pointPolygonTest(cross_poly_np, center, True)
                if dist >= 0 or abs(dist) < 25:
                    print(f"[CROSS] Stop tæt på kryds (dist={dist:.1f})")
                    continue

            # === Styr robot mod bold ===
            reached_ball = move_towards_ball(front, back, balls)
            if reached_ball:
                print("[TRACK] Bold er nået, stopper motor og aktiverer claw.")
                stop_ev3()
                pick_up_sequence(cap, matrix)
                reset_stop_state()

                collected_balls += 1
                if collected_balls >= MAX_BALLS:
                    print("[track] Maks antal bolde samlet.")
                    stop_ev3()
                    go_to_goal(goal_b, front, back)
                    break
                continue

        # === VISUALISERING ===
        for label, (x, y) in all_balls:
            pt = (x, y)
            if is_outside_all_polygons(pt, arena_np, cross_poly_np):
                color = COLOR_BGR.get(label, (200, 200, 200))
                cv2.circle(warped, pt, 10, color, 2)
            else:
                cv2.circle(warped, pt, 10, (0, 0, 255), 1)  # rød = forbudt område

        if cross_poly is not None:
            poly = np.array([cross_poly_np], dtype=np.int32)
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
