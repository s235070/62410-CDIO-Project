import cv2
import numpy as np
import threading
import time
import math
import paramiko

# EV3 SSH details
EV3_IP = "172.20.10.8"
EV3_USER = "robot"

class EV3SSH:
    """Manages a persistent SSH connection to EV3 for real-time execution."""
    def __init__(self, ip, user):
        self.ip = ip
        self.user = user
        self.client = None
        self.lock = threading.Lock()
        self.prev_command = None
        self.last_command_time = 0
        self.connect()

    def connect(self):
        """Establish a persistent SSH connection."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.ip, username=self.user)
            print("[INFO] Connected to EV3!")
        except Exception as e:
            print("[ERROR] SSH Connection Failed:", e)

    def send_command(self, command):
        """Send motor commands to EV3 only if changed."""
        with self.lock:
            current_time = time.time()
            if command != self.prev_command or (command == "STOP" and current_time - self.last_command_time > 1.5):
                try:
                    self.client.exec_command(f"echo {command} > /home/robot/motor_command.txt")
                    print(f"[EV3] Command Sent: {command}")
                    self.prev_command = command
                    self.last_command_time = current_time
                except Exception as e:
                    print("[ERROR] SSH Command Failed:", e)

    def stop(self):
        """Stop EV3 safely."""
        self.send_command("STOP")

# Initialize SSH connection
ev3 = EV3SSH(EV3_IP, EV3_USER)

# Open camera
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Fejl: Kamera kunne ikke åbnes!")
    exit()

# Camera settings
FRAME_WIDTH = int(cap.get(3))
FRAME_HEIGHT = int(cap.get(4))
CENTER_X = FRAME_WIDTH // 2  # The middle of the screen
SAFE_DISTANCE = 120  # Stop when this close
CENTER_TOLERANCE = 30  # How centered the ball must be to go forward

ball_x_values = []
last_movement = None  

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kan ikke modtage frame fra kamera. Afslutter...")
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define color ranges
    lower_orange, upper_orange = np.array([10, 100, 100]), np.array([25, 255, 255])
    lower_green, upper_green = np.array([40, 40, 40]), np.array([80, 255, 255])

    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    contours_orange, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    ball_detected, ev3_detected = False, False
    ball_x, ball_y, ev3_x, ev3_y = None, None, None, None

    # Detect the ball
    if contours_orange:
        largest_orange = max(contours_orange, key=cv2.contourArea)
        if cv2.contourArea(largest_orange) > 120:  # Avoid noise
            M_orange = cv2.moments(largest_orange)
            if M_orange["m00"] > 0:
                ball_x = int(M_orange["m10"] / M_orange["m00"])
                ball_y = int(M_orange["m01"] / M_orange["m00"])
                ball_detected = True
                cv2.drawContours(frame, [largest_orange], -1, (0, 165, 255), 2)
                cv2.circle(frame, (ball_x, ball_y), 5, (0, 165, 255), -1)

    # Detect the EV3 robot
    if contours_green:
        largest_green = max(contours_green, key=cv2.contourArea)
        if cv2.contourArea(largest_green) > 120:
            M_green = cv2.moments(largest_green)
            if M_green["m00"] > 0:
                ev3_x = int(M_green["m10"] / M_green["m00"])
                ev3_y = int(M_green["m01"] / M_green["m00"])
                ev3_detected = True
                cv2.drawContours(frame, [largest_green], -1, (0, 255, 0), 2)
                cv2.circle(frame, (ev3_x, ev3_y), 5, (0, 255, 0), -1)

    if ball_detected and ev3_detected:
        cv2.line(frame, (ev3_x, ev3_y), (ball_x, ball_y), (255, 0, 0), 3)

        # Calculate the distance
        distance = math.hypot(ball_x - ev3_x, ball_y - ev3_y)

        # Moving average filter for ball position
        ball_x_values.append(ball_x)
        if len(ball_x_values) > 5:
            ball_x_values.pop(0)
        ball_x_avg = sum(ball_x_values) // len(ball_x_values)

        print(f"[DEBUG] Ball X (Avg): {ball_x_avg}, EV3 X: {ev3_x}, Distance: {distance} | Center X: {CENTER_X}")

        # **Check if the ball is centered**
        if abs(ball_x_avg - CENTER_X) <= CENTER_TOLERANCE and distance > SAFE_DISTANCE:
            ev3.send_command("FORWARD")
            last_movement = "FORWARD"

        # **Stop when close enough**
        elif distance < SAFE_DISTANCE:
            ev3.stop()
            last_movement = "STOP"

    else:
        ev3.stop()
        last_movement = "STOP"

    cv2.imshow('Kamera', frame)
    cv2.imshow('Mask Orange & Green', mask_orange | mask_green)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ev3.client.close()
