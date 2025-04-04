# ev3_track.py
import cv2
import numpy as np
import math
import time
from ev3_commander import EV3Controller

# Tilslut til EV3 via SSH
ev3 = EV3Controller("192.168.0.30", "robot")

# --- FARVEGRÆNSER ---
white_ball_lower  = np.array([0, 0, 170])
white_ball_upper  = np.array([180, 65, 255])

front_dot_lower = np.array([25, 15, 90])    # mørk markør
front_dot_upper = np.array([55, 65, 170])
blue_back_lower = np.array([95, 50, 150])   # blå bag-markør
blue_back_upper = np.array([110, 210, 230])

# Hjælpefunktioner
def find_center(mask):
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if cnts:
        c = max(cnts, key=cv2.contourArea)
        if cv2.contourArea(c) > 20:
            M = cv2.moments(c)
            if M["m00"] != 0:
                return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    return None

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

# Kamera
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("❌ Could not open camera")
    exit()

last_command_time = 0
command_delay = 1.2  # sekunder

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Find EV3 markører
    front = find_center(cv2.inRange(hsv, front_dot_lower, front_dot_upper))
    back  = find_center(cv2.inRange(hsv, blue_back_lower, blue_back_upper))

    # Find hvide bolde
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 1)
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.6,
        minDist=10,
        param1=60,
        param2=20,
        minRadius=2,
        maxRadius=12
    )

    white_balls = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for (cx, cy, r) in circles[0, :]:
            roi_size = int(r * 0.6)
            x1, x2 = max(0, cx - roi_size), min(frame.shape[1], cx + roi_size)
            y1, y2 = max(0, cy - roi_size), min(frame.shape[0], cy + roi_size)
            roi_hsv = hsv[y1:y2, x1:x2]
            mask = cv2.inRange(roi_hsv, white_ball_lower, white_ball_upper)
            score = cv2.countNonZero(mask)
            if score > 8:
                white_balls.append((cx, cy))
                cv2.circle(frame, (cx, cy), r, (255, 255, 255), 2)

    if front and back:
        # Beregn robotposition og retning
        mid = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)
        cv2.arrowedLine(frame, back, front, (255, 0, 255), 3)

        dx = front[0] - back[0]
        dy = front[1] - back[1]
        heading = math.atan2(dy, dx)

        if white_balls:
            nearest = min(white_balls, key=lambda b: distance(mid, b))
            dxb = nearest[0] - mid[0]
            dyb = nearest[1] - mid[1]
            angle_to_ball = math.atan2(dyb, dxb)
            diff_rad = angle_to_ball - heading
            diff_deg = math.degrees(diff_rad)
            dist_px = distance(mid, nearest)

            # Tegn visualisering
            cv2.line(frame, mid, nearest, (0, 255, 255), 2)
            cv2.putText(frame, f"{int(diff_deg)} deg | {int(dist_px)} px",
                        (mid[0]+10, mid[1]+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # --- STYRING ---
            print(f"[INFO] Angle to ball: {diff_deg:.2f}, Distance: {dist_px:.2f}")

            if time.time() - last_command_time > command_delay:
                if abs(diff_deg) > 15:
                    cmd = f"turn {int(diff_deg)}"
                    ev3.send(cmd)
                elif dist_px > 50:
                    cmd = f"forward {int(dist_px)}"
                    ev3.send(cmd)
                else:
                    print("[WAIT] No movement needed")

                last_command_time = time.time()
            else:
                print("[WAIT] Waiting before sending new command")

    cv2.imshow("GolfBot", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ev3.close()
