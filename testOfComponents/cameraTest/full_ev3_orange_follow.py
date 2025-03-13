#!/usr/bin/env python3

import cv2
import numpy as np
import subprocess
import time

# CONFIGURATION
EV3_IP = "172.20.10.8"  # IP address of your EV3 brick
REMOTE_SCRIPT = "/home/robot/62410-CDIO-Project/testOfComponents/cameraTest/move_robot.py"  # Path to move_robot.py on the EV3
CAMERA_INDEX = 1  # Camera index (1 for USB camera)
LOWER_ORANGE = np.array([10, 100, 100])  # Lower bound of the orange color in HSV space
UPPER_ORANGE = np.array([25, 255, 255])  # Upper bound of the orange color in HSV space
AREA_CLOSE_THRESHOLD = 2000  # Minimum area threshold to detect ball as close
LEFT_BOUND_RATIO = 0.4  # Left boundary ratio of the frame
RIGHT_BOUND_RATIO = 0.6  # Right boundary ratio of the frame
LOOP_DELAY = 0.1  # Time in seconds between each iteration

# Utility function to send command to EV3 (e.g., move forward, left, right, stop)
def send_command(cmd):
    try:
        subprocess.run([
            "ssh", f"robot@{EV3_IP}",
            "python3", REMOTE_SCRIPT, cmd
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error sending command '{cmd}' to EV3: {e}")

# Main function for detecting the ball and controlling the robot
def main():
    # Open the camera on your laptop
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"Cannot open camera at index {CAMERA_INDEX}")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    print("Starting camera loop. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera read failed.")
            break

        # Convert the frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask for the orange color
        mask = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest contour (assumed to be the ball)
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)

            if area > 100:  # Ignore small contours
                # Get the bounding box around the largest contour
                x, y, w, h = cv2.boundingRect(c)
                cx = x + w // 2  # Center x-coordinate
                cy = y + h // 2  # Center y-coordinate

                # Draw the bounding box and the center point
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                cv2.putText(frame, f"Area:{area}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Decide the robot's movement based on the ball's position
                if area > AREA_CLOSE_THRESHOLD:
                    # Ball is close, stop the robot
                    send_command("stop")
                else:
                    left_boundary = frame_width * LEFT_BOUND_RATIO
                    right_boundary = frame_width * RIGHT_BOUND_RATIO

                    if cx < left_boundary:
                        # Ball is to the left, turn left
                        send_command("left")
                    elif cx > right_boundary:
                        # Ball is to the right, turn right
                        send_command("right")
                    else:
                        # Ball is in the center, move forward
                        send_command("forward")
            else:
                send_command("stop")  # Stop if ball is too small to track
        else:
            send_command("stop")  # Stop if no ball is detected

        # Show the image with the mask and ball detection
        cv2.imshow('Frame', frame)
        cv2.imshow('Mask', mask)

        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Delay to control loop speed
        time.sleep(LOOP_DELAY)

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    send_command("stop")  # Stop the robot after exiting the loop
    print("Exiting script.")

if __name__ == "__main__":
    main()
