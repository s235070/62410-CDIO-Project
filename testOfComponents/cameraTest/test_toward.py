# -*- coding: utf-8 -*-
import cv2
import numpy as np
import paramiko
import threading
import time

# EV3 SSH details
EV3_IP = "172.20.10.6"
EV3_USER = "robot"

class EV3SSH:
    """Manages a persistent SSH connection to EV3 for real-time execution."""
    def __init__(self, ip, user):
        self.ip = ip
        self.user = user
        self.client = None
        self.ev3_is_moving = False
        self.lock = threading.Lock()
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
        """Move EV3 forward."""
        if not self.ev3_is_moving:
            print("Moving forward!")
            self.send_command("FORWARD")
            self.ev3_is_moving = True

    def move_left(self):
        """Turn EV3 left to center the ball."""
        print("Turning left!")
        self.send_command("LEFT")

    def move_right(self):
        """Turn EV3 right to center the ball."""
        print("Turning right!")
        self.send_command("RIGHT")

    def stop(self):
        """Stop EV3."""
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

# Open camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Fejl: Kamera 1 kunne ikke åbnes! Sørg for, at det er tilsluttet.")
    exit()

FRAME_WIDTH = int(cap.get(3))  # Get frame width
CENTER_X = FRAME_WIDTH // 2    # Calculate center of the screen

# Stop when the EV3 marker is close to the ball
SAFE_DISTANCE = 100  # Minimum safe distance between the ball and EV3

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kan ikke modtage frame fra kamera 1. Afslutter...")
        break

    # Convert frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define color ranges
    lower_orange = np.array([10, 100, 100])    # Orange ball
    upper_orange = np.array([25, 255, 255])

    lower_blue = np.array([100, 150, 50])  # Navy blue marker on EV3
    upper_blue = np.array([130, 255, 255])

    # Create masks
    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Find contours for the ball
    contours_orange, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    ball_detected = False
    ev3_detected = False
    ball_x = None
    ev3_x = None
    distance = None

    # Find the largest orange ball contour
    if contours_orange:
        largest_ball = max(contours_orange, key=cv2.contourArea)
        M_ball = cv2.moments(largest_ball)
        
        if M_ball["m00"] > 0:
            ball_x = int(M_ball["m10"] / M_ball["m00"])  # Get x position of the ball
            ball_y = int(M_ball["m01"] / M_ball["m00"])  # Get y position
            ball_detected = True

    # Find the largest navy blue EV3 contour
    if contours_blue:
        largest_ev3 = max(contours_blue, key=cv2.contourArea)
        M_ev3 = cv2.moments(largest_ev3)

        if M_ev3["m00"] > 0:
            ev3_x = int(M_ev3["m10"] / M_ev3["m00"])  # Get x position of EV3
            ev3_y = int(M_ev3["m01"] / M_ev3["m00"])  # Get y position
            ev3_detected = True

    # Calculate distance between EV3 and the ball
    if ball_detected and ev3_detected:
        distance = abs(ev3_y - ball_y)  # Distance based on y-coordinates (height)

    # Control movement based on ball position and EV3 location
    if ball_detected and ev3_detected:
        if distance < SAFE_DISTANCE:
            ev3.stop()  # Stop when the EV3 is close enough
        else:
            if ball_x < CENTER_X - 50:  # Ball is too far left
                ev3.move_left()
            elif ball_x > CENTER_X + 50:  # Ball is too far right
                ev3.move_right()
            else:
                ev3.move_forward()  # Ball is centered, move forward
    else:
        ev3.stop()  # No ball or EV3 detected, stop

    # Show camera feed
    cv2.imshow('Kamera', frame)
    cv2.imshow('Ball Mask', mask_orange)
    cv2.imshow('EV3 Mask', mask_blue)

    # Prevent freezing
    cv2.waitKey(1)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
ev3.close()
