# pickup_ball.py

import time
import numpy as np
import cv2

from ev3_control import send_safe_command, CMD_FORWARD_SLIGHT, CMD_BACKWARD_SLIGHT, CMD_BACK_A_LITTLE
from track.track_balls import detect_balls_yolo
from track.track_ev3 import detect_ev3

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

def pick_up_sequence(cap, matrix):
    print("[PICKUP] Starter finjustering mod bolden...")

    timeout = time.time() + 5  # Max 5 sekunders finjustering
    while time.time() < timeout:
        frame = cap.read()
        if frame is None:
            continue

        warped = cv2.warpPerspective(frame, matrix, (640, 480))
        balls = detect_balls_yolo(warped)
        front, back, *_ = detect_ev3(warped)

        if not front or not back or not balls:
            # Vis alligevel billedet
            cv2.imshow("Arena View", warped)
            cv2.waitKey(1)
            continue

        # Find center og nærmeste bold
        center = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)
        balls.sort(key=lambda b: np.hypot(center[0] - b[1][0], center[1] - b[1][1]))
        _, (bx, by) = balls[0]

        # Tegn visuelt overlay
        cv2.circle(warped, (bx, by), 10, (0, 140, 255), 2)
        cv2.circle(warped, center, 8, (255, 255, 0), 2)
        cv2.line(warped, center, (bx, by), (0, 255, 255), 1)

        # Vis live
        cv2.imshow("Arena View", warped)
        cv2.waitKey(1)

        # Bevæg mod bolden
        dx = bx - center[0]
        dy = by - center[1]
        dist = np.hypot(dx, dy)

        if dist < 12:  # ← ALT FOR TÆT PÅ → bak lidt!
            print(f"[PICKUP] EV3 er for tæt på bolden (dist={dist:.1f}) → BACK A LITTLE")
            send_safe_command(CMD_BACK_A_LITTLE)
            time.sleep(0.8)
            continue

        if abs(dx) < 10 and abs(dy) < 10:
            print("[PICKUP] Bold er centreret.")
            break

        if dy < -15:
            send_safe_command(CMD_FORWARD_SLIGHT)
        elif dy > 15:
            send_safe_command(CMD_BACKWARD_SLIGHT)

        time.sleep(0.7)