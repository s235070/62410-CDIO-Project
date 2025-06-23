import cv2
import numpy as np
import time
from config import CAMERA_INDEX, WARP_WIDTH, WARP_HEIGHT
from utils.vision import warp_image
from track.input_handler import ask_for_label, load_matrix
from track.track_arena import select_detection_zone, create_manual_mask
from track.track_balls import detect_balls_yolo, COLOR_BGR
from track.track_ev3 import detect_ev3
from track.track_cross import load_cross_polygon
from track.track_goal import draw_goals  # 🥅 NYT
from ev3_control import send_command, setup_connection, CMD_FORWARD, CMD_LEFT, CMD_RIGHT

last_cmd = None
command_cooldown = 0
CMD_DELAY_FRAMES = 8

def main():
    global last_cmd, command_cooldown
    setup_connection()

    label = ask_for_label().strip().lower()
    matrix = load_matrix(label)
    if matrix is None:
        return

    cross_poly = load_cross_polygon(label)
    if cross_poly is None:
        print("[WARN] No cross polygon found — robot will ignore the cross.")

    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("[ERROR] Camera not accessible")
        return

    print("[INFO] Waiting for frame to define detection zone...")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        cv2.imshow("Warped Preview", warped)
        if cv2.waitKey(1) & 0xFF == ord("s"):
            break

    arena_polygon = select_detection_zone(warped)
    arena_mask = create_manual_mask(arena_polygon, warped.shape[:2])
    cv2.destroyWindow("Warped Preview")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        warped = draw_goals(warped)  # 🥅 Tegn mål

        balls = detect_balls_yolo(warped)

        if cross_poly is not None:
            cross_poly_int = np.array([cross_poly], dtype=np.int32)
            cv2.polylines(warped, [cross_poly_int], True, (0, 0, 255), 2)
            cx, cy = np.mean(cross_poly, axis=0).astype(int)
            cv2.putText(warped, "CROSS", (cx + 10, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        for label, (x, y) in balls:
            color = COLOR_BGR.get(label, (200, 200, 200))
            cv2.circle(warped, (x, y), 10, color, 2)

        front, back, *_ = detect_ev3(warped)
        if front and back:
            ev3_center = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)

            if cross_poly is not None:
                dist = cv2.pointPolygonTest(cross_poly.astype(np.float32), ev3_center, True)
                if dist >= 0 or abs(dist) < 25:
                    print(f"[CROSS] Too close to cross → Stop (distance: {dist:.1f})")
                    send_command(None)
                    last_cmd = None
                    continue

            cv2.circle(warped, front, 8, (0, 255, 0), 2)
            cv2.circle(warped, back, 8, (255, 0, 0), 2)
            cv2.line(warped, front, back, (0, 255, 255), 2)

            dx, dy = front[0] - back[0], front[1] - back[1]
            vx, vy = dx, dy

            nearest_ball = None
            min_dist = float("inf")
            for _, (bx, by) in balls:
                dist = np.hypot(back[0] - bx, back[1] - by)
                if dist < 45:
                    continue
                if dist < min_dist:
                    min_dist = dist
                    nearest_ball = (bx, by)

            if nearest_ball:
                cv2.line(warped, front, nearest_ball, (0, 255, 255), 2)
                ux, uy = nearest_ball[0] - front[0], nearest_ball[1] - front[1]
                dot = vx * ux + vy * uy
                det = vx * uy - vy * ux
                angle_diff = np.degrees(np.arctan2(det, dot))

                if abs(angle_diff) > 3 or min_dist < 70:
                    print(f"[EV3] Vinkel: {angle_diff:.1f}°, Afstand: {min_dist:.0f}")

                cmd = None
                if min_dist < 60:
                    print("[CMD] Tæt på → Stop")
                    last_cmd = None
                elif angle_diff > 20:
                    print("[CMD] Drej HØJRE")
                    cmd = CMD_RIGHT
                elif angle_diff < -20:
                    print("[CMD] Drej VENSTRE")
                    cmd = CMD_LEFT
                else:
                    print("[CMD] Kør FREM")
                    cmd = CMD_FORWARD

                if cmd and (cmd != last_cmd or command_cooldown <= 0):
                    send_command(cmd)
                    time.sleep(0.1)
                    last_cmd = cmd
                    command_cooldown = CMD_DELAY_FRAMES

        if command_cooldown > 0:
            command_cooldown -= 1

        cv2.polylines(warped, [arena_polygon], True, (180, 0, 180), 2)
        cv2.imshow("Arena View", warped)
        cv2.imshow("Arena Mask", arena_mask)

        if cv2.waitKey(10) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
