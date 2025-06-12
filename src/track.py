import cv2
import numpy as np
import time
from config import CAMERA_INDEX, WARP_WIDTH, WARP_HEIGHT
from utils.vision import warp_image
from track.input_handler import ask_for_label, load_matrix
from track.track_arena import select_detection_zone, create_manual_mask
from track.track_balls import detect_balls_yolo, COLOR_BGR
from track.track_ev3 import detect_ev3
from ev3_control import send_command, setup_connection, CMD_FORWARD, CMD_LEFT, CMD_RIGHT

# Cooldown-styring
last_cmd = None
command_cooldown = 0
CMD_DELAY_FRAMES = 8

def main():
    global last_cmd, command_cooldown
    setup_connection()

    label = ask_for_label()
    matrix = load_matrix(label)
    if matrix is None:
        return

    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Camera not accessible")
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
        balls = detect_balls_yolo(warped)

        for label, (x, y) in balls:
            color = COLOR_BGR.get(label, (200, 200, 200))
            cv2.circle(warped, (x, y), 10, color, 2)

        front, back = detect_ev3(warped)
        if front and back:
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
                    time.sleep(0.1)  # ← tilføj denne
                    last_cmd = cmd
                    command_cooldown = CMD_DELAY_FRAMES

        # Cooldown reduceres
        if command_cooldown > 0:
            command_cooldown -= 1

        # Visualisering
        cv2.polylines(warped, [arena_polygon], isClosed=True, color=(180, 0, 180), thickness=2)
        cv2.imshow("Arena View", warped)
        cv2.imshow("Arena Mask", arena_mask)

        if cv2.waitKey(10) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
