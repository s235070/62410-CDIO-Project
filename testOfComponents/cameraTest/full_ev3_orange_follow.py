#!/usr/bin/env python3

import cv2
import numpy as np
import subprocess
import time

#############################################################################
# CONFIG - ADJUST THESE FOR YOUR SETUP
#############################################################################

# The IP address (or hostname) of your EV3
EV3_IP = "172.20.10.8"  

# The path to move_robot.py on the EV3
REMOTE_SCRIPT = "/home/robot/62410-CDIO-Project/testOfComponents/cameraTest/move_robot.py"

# Camera index on your laptop (0 = built-in, 1 = USB, etc.)
CAMERA_INDEX = 1

# HSV range for detecting orange
# Adjust if your lighting/orange shade is different
LOWER_ORANGE = np.array([10, 100, 100])
UPPER_ORANGE = np.array([25, 255, 255])

# If the ball's area is above this, we consider it "close"
AREA_CLOSE_THRESHOLD = 2000

# We'll define a left/right dead zone boundaries
# If center_x is within [0.4 * frame_width, 0.6 * frame_width], we go forward
LEFT_BOUND_RATIO = 0.4
RIGHT_BOUND_RATIO = 0.6

# Optional: how many times per second we run the loop
LOOP_DELAY = 0.1  # 0.1s ~ 10 times/sec

#############################################################################
# UTILITY FUNCTION TO SEND COMMAND TO EV3
#############################################################################

def send_command(cmd):
    """
    Calls move_robot.py on the EV3 via SSH, passing a command like 'forward', 'left', 'right', or 'stop'.
    """
    try:
        subprocess.run([
            "ssh", f"robot@{EV3_IP}",
            "python3", REMOTE_SCRIPT, cmd
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error sending command '{cmd}' to EV3: {e}")

#############################################################################
# MAIN SCRIPT
#############################################################################

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

        # Convert to HSV for color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a binary mask for "orange"
        mask = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Largest contour
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)

            if area > 100:  # ignore tiny noise
                # Get bounding box
                x, y, w, h = cv2.boundingRect(c)
                cx = x + w//2
                cy = y + h//2

                # Draw
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                cv2.putText(frame, f"Area:{area}", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

                # Decide how to move the EV3
                if area > AREA_CLOSE_THRESHOLD:
                    # Ball is "close" => STOP
                    send_command("stop")
                else:
                    # Check if ball is left/right/center
                    left_boundary = frame_width * LEFT_BOUND_RATIO
                    right_boundary = frame_width * RIGHT_BOUND_RATIO

                    if cx < left_boundary:
                        send_command("left")
                    elif cx > right_boundary:
                        send_command("right")
                    else:
                        # Center region => forward
                        send_command("forward")
            else:
                # Contour is too small => maybe stop or keep searching
                send_command("stop")
        else:
            # No ball => stop or maybe do a search turn
            send_command("stop")

        # Show images
        cv2.imshow('Frame', frame)
        cv2.imshow('Mask', mask)

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(LOOP_DELAY)

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    # Final stop
    send_command("stop")
    print("Exiting script.")

if __name__ == "__main__":
    main()
