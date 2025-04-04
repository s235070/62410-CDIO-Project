import cv2
import numpy as np
import socket
import time

# ============== EV3 Connection Setup ==============
EV3_IP = '192.168.0.30'  # your EV3’s IP on same WiFi
EV3_PORT = 999
ev3_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ev3_sock.connect((EV3_IP, EV3_PORT))
# ===================================================

def send_command(cmd):
    """
    Sends simple text commands like 'LEFT','RIGHT','FORWARD','STOP'
    to the EV3 over the socket.
    """
    ev3_sock.send((cmd + '\n').encode())

# Example color ranges for an orange ball and white ball
orange_lower = np.array([5, 140, 140])
orange_upper = np.array([25, 255, 255])

white_lower  = np.array([0, 0, 220])
white_upper  = np.array([180, 40, 255])

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to HSV for color
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # A) Find the orange/white balls using color + shape (HoughCircles)
    # 1) Build color masks
    mask_orange = cv2.inRange(hsv, orange_lower, orange_upper)
    mask_white  = cv2.inRange(hsv, white_lower,  white_upper)

    # 2) For shape detection, go grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 1)

    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.6,
        minDist=15,
        param1=70,
        param2=25,
        minRadius=2,
        maxRadius=10
    )

    # We'll track only 1 ball, e.g. the first circle
    ball_cx = None
    ball_cy = None

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for (cx, cy, r) in circles[0, :]:
            # Check color in the circle region
            roi_size = int(r * 0.6)
            x1, x2 = max(0, cx - roi_size), min(frame.shape[1], cx + roi_size)
            y1, y2 = max(0, cy - roi_size), min(frame.shape[0], cy + roi_size)

            roi_hsv = hsv[y1:y2, x1:x2]
            o_score = cv2.countNonZero(cv2.inRange(roi_hsv, orange_lower, orange_upper))
            w_score = cv2.countNonZero(cv2.inRange(roi_hsv, white_lower,  white_upper))

            # If either is big enough, assume it's a ball
            if o_score > 20 or w_score > 20:
                # We'll pick the first such circle
                ball_cx, ball_cy = cx, cy
                color_draw = (0,140,255) if o_score > w_score else (255,255,255)
                label = "VIP" if o_score> w_score else "White"
                cv2.circle(frame, (cx,cy), r, color_draw,2)
                cv2.circle(frame, (cx,cy), 2, color_draw, -1)
                cv2.putText(frame, label, (cx-10, cy-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_draw,2)
                break  # just track the first ball found

    # B) Steering logic if we found a ball
    # For a simple approach, we compare the ball's x with the center
    h, w = frame.shape[:2]
    center_x = w // 2
    offset = 40  # tolerance zone around center

    if ball_cx is not None:
        dx = ball_cx - center_x
        if dx < -offset:
            send_command("LEFT")
        elif dx > offset:
            send_command("RIGHT")
        else:
            # we're aligned horizontally -> move forward
            send_command("FORWARD")
    else:
        # No ball found => STOP
        send_command("STOP")

    cv2.imshow("Laptop Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

send_command("STOP")
cap.release()
ev3_sock.close()
cv2.destroyAllWindows()
