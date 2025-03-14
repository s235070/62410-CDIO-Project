import cv2
import numpy as np
import os

# EV3 SSH details
EV3_IP = "172.20.10.8"
EV3_USER = "robot"

def send_ev3_command(command):
    """Send a shell command to the EV3 via SSH (only when needed)"""
    full_command = f'ssh {EV3_USER}@{EV3_IP} "python3 -c \'{command}\'"'
    print(f"Executing SSH Command: {full_command}")  # Debug print
    os.system(full_command)

# Open PC camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera.")
    exit()

# Track whether the EV3 is currently moving
ev3_is_moving = False

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame. Exiting...")
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

    # Only send SSH command if the state has changed
    if ball_detected and not ev3_is_moving:
        print("Orange ball detected! Moving forward.")
        send_ev3_command("from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C; tank=MoveTank(OUTPUT_B, OUTPUT_C); tank.on(30,30)")
        ev3_is_moving = True

    elif not ball_detected and ev3_is_moving:
        print("No ball detected. Stopping.")
        send_ev3_command("from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C; tank=MoveTank(OUTPUT_B, OUTPUT_C); tank.off()")
        ev3_is_moving = False

    # Show camera feed
    cv2.imshow('Camera', frame)
    cv2.imshow('Mask', mask)

    # Prevent freezing
    cv2.waitKey(1)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
send_ev3_command("from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C; tank=MoveTank(OUTPUT_B, OUTPUT_C); tank.off()")
