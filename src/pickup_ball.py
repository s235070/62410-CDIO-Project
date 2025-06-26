# pickup_ball.py

import time
import numpy as np
import cv2

from ev3_control import send_safe_command, CMD_FORWARD_SLIGHT, CMD_BACKWARD_SLIGHT, CMD_BACK_A_LITTLE
from track.track_balls import detect_balls_yolo
from track.track_ev3 import detect_ev3
from ev3_move import stop_ev3
from track.track_balls import COLOR_BGR  
def open_claw():
    send_safe_command("python3 move_robot.py open_claw")
    print("[CLAW] Åbner kløerne...")

def close_claw():
    send_safe_command("python3 move_robot.py close_claw")
    print("[CLAW] Lukker kløerne...")

def push_ball():
    send_safe_command("python3 move_robot.py push_ball")
    print("[PUSHER] Skubber bolden...")

def slow_forward():
    send_safe_command("python3 move_robot.py slow_forward")
    print("[MOVE] Kører langsomt frem...")

def spin_left():
    send_safe_command("python3 move_robot.py spin_left")
    print("[MOVE] Drejer lidt til venstre...")

def spin_right():
    send_safe_command("python3 move_robot.py spin_right")
    print("[MOVE] Drejer lidt til højre...")

def back_a_little():
    send_safe_command("python3 move_robot.py back_a_little")
    print("[MOVE] Bakker lidt...")


def pick_up_sequence(cap, matrix):
    print("[PICKUP] Starter finjustering...")

    timeout = time.time() + 6
    best_ball = None
    front = back = None

    while time.time() < timeout:
        frame = cap.read()
        if frame is None:
            continue

        warped = cv2.warpPerspective(frame, matrix, (640, 480))
        balls = detect_balls_yolo(warped)
        print("[YOLO DEBUG] Fundne bolde:", balls)

        front, back, *_ = detect_ev3(warped)
        if not front or not back or not balls:
            cv2.imshow("Arena View", warped)
            cv2.waitKey(1)
            continue

        ev3_center = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)

        # 🔴 Fjern bolde for tæt på EV3 (fx under 60 pixels)
        balls = [b for b in balls if np.hypot(b[1][0] - ev3_center[0], b[1][1] - ev3_center[1]) > 60]
        if not balls:
            print("[PICKUP] Ingen gyldige bolde (alle for tæt på EV3).")
            break

        # Vælg nærmeste bold
        balls.sort(key=lambda b: np.hypot(ev3_center[0] - b[1][0], ev3_center[1] - b[1][1]))
        label, (bx, by) = balls[0]
        best_ball = (bx, by)

        vx, vy = front[0] - back[0], front[1] - back[1]
        ux, uy = bx - front[0], by - front[1]

        dot = vx * ux + vy * uy
        det = vx * uy - vy * ux
        angle = np.degrees(np.arctan2(det, dot))
        dist = np.hypot(bx - ev3_center[0], by - ev3_center[1])

        # === VISUALISERING ===
        warped_debug = warped.copy()
        for lbl, (x, y) in balls:
            color = COLOR_BGR.get(lbl, (0, 255, 255))
            cv2.circle(warped_debug, (x, y), 10, color, 1)

        target_color = COLOR_BGR.get(label, (0, 255, 0))
        cv2.circle(warped_debug, (bx, by), 10, target_color, 2)
        cv2.circle(warped_debug, ev3_center, 8, (255, 0, 0), 2)
        cv2.line(warped_debug, ev3_center, (bx, by), (200, 200, 200), 1)

        cv2.imshow("Arena View", warped_debug)
        cv2.waitKey(1)

        print(f"[PICKUP-ALIGN] angle={angle:.1f}, dist={dist:.1f}")

        if dist < 20:
            print("[PICKUP] Tæt nok på bold → stop justering")
            break
        elif abs(angle) > 10:
            print(f"[PICKUP] Drejer mod bold (vinkel: {angle:.1f})")
            if angle > 0:
                spin_right()
            else:
                spin_left()
        else:
            print("[PICKUP] Bold centreret → kør frem")
            slow_forward()

        time.sleep(0.6)

    if best_ball is None:
        print("[PICKUP] Bold ikke fundet. Afbryder.")
        return

    # === OPSAMLING ===
    print("[PICKUP] Finjusterer retning inden opsamling...")
    vx, vy = front[0] - back[0], front[1] - back[1]
    ux, uy = best_ball[0] - front[0], best_ball[1] - front[1]
    dot = vx * ux + vy * uy
    det = vx * uy - vy * ux
    angle = np.degrees(np.arctan2(det, dot))

    if abs(angle) > 8:
        print(f"[PICKUP-FIX] Retter retning mod bold (angle={angle:.1f})")
        if angle > 0:
            spin_right()
        else:
            spin_left()
        time.sleep(0.4)

    print("[PICKUP] Samler bold op...")
    stop_ev3()
    time.sleep(0.4)

    back_a_little()
    time.sleep(0.6)

    open_claw()
    time.sleep(0.5)

    slow_forward()
    time.sleep(1.1)

    close_claw()
    time.sleep(0.6)

    stop_ev3()
    print("[PICKUP] Bold samlet.")
