import cv2
import numpy as np
import paramiko
import threading
import time

# EV3 SSH details
EV3_IP = "192.168.137.115"
EV3_USER = "robot"

class EV3SSH:
    """Manages a persistent SSH connection to EV3 for real-time execution."""
    def __init__(self, ip, user):
        self.ip = ip
        self.user = user
        self.client = None
        self.ev3_is_moving = False  # Track motor state to avoid duplicate commands
        self.lock = threading.Lock()  # Prevent SSH command conflicts
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
        """Write motor commands to the EV3 control file for instant execution."""
        with self.lock:
            try:
                self.client.exec_command("echo {} > /home/robot/motor_command.txt".format(command))
            except Exception as e:
                print("[ERROR] SSH Command Failed:", e)

    def move_forward(self):
        """Move EV3 forward instantly without lag."""
        if not self.ev3_is_moving:
            print("Moving forward!")
            self.send_command("FORWARD")
            self.ev3_is_moving = True

    def stop(self):
        """Stop EV3 instantly without lag."""
        if self.ev3_is_moving:
            print("Stopping robot!")
            self.send_command("STOP")
            self.ev3_is_moving = False

    def close(self):
        """Close SSH connection."""
        self.send_command("STOP")
        if self.client:
            self.client.close()
            print("[INFO] SSH Connection Closed.")

# Initialize persistent SSH connection
ev3 = EV3SSH(EV3_IP, EV3_USER)

# Open camera interface 1
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Fejl: Kamera 1 kunne ikke åbnes! Sørg for, at det er tilsluttet.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kan ikke modtage frame fra kamera 1. Afslutter...")
        break

    # Convert frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define orange color range
    lower_orange = np.array([10, 100, 100])
    upper_orange = np.array([25, 255, 255])

    # Create a mask
    mask = cv2.inRange(hsv, lower_orange, upper_orange)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    ball_detected = False
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        if area > 100:
            ball_detected = True

    # Only send commands if necessary
    if ball_detected:
        ev3.move_forward()
    else:
        ev3.stop()

    # Show camera feed
    cv2.imshow('Kamera', frame)
    cv2.imshow('Maske', mask)

    # Prevent freezing
    cv2.waitKey(1)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
ev3.close()
