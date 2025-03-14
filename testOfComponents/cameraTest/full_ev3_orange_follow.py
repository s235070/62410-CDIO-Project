import cv2
import numpy as np
import subprocess
import time

# Configuration - Adjust for your setup
EV3_IP = "172.20.10.8"  # Change to your EV3 IP
REMOTE_SCRIPT = "/home/robot/62410-CDIO-Project/testOfComponents/cameraTest/move_robot.py"  # Path to your move_robot.py on EV3
CAMERA_INDEX = 0  # Adjust based on your setup (0 = built-in camera, 1 = USB camera, etc.)

# HSV range for detecting orange
LOWER_ORANGE = np.array([10, 100, 100])
UPPER_ORANGE = np.array([25, 255, 255])

# Area threshold to consider ball "close"
AREA_CLOSE_THRESHOLD = 2000

# Left/right bounds
LEFT_BOUND_RATIO = 0.4
RIGHT_BOUND_RATIO = 0.6

# Delay between frames
LOOP_DELAY = 0.1

def send_command(cmd):
    """
    Sends a command to the EV3 to control its movement via SSH.
    """
    try:
        subprocess.run(["ssh", f"robot@{EV3_IP}", "python3", REMOTE_SCRIPT, cmd], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error sending command '{cmd}' to EV3: {e}")

def main():
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

        # Convert the frame to HSV color space for orange detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create mask for orange color
        mask = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)

        # Find contours of the orange region
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Get the largest contour
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)

            if area > 100:  # Ignore small contours (noise)
                x, y, w, h = cv2.boundingRect(c)
                cx = x + w // 2
                cy = y + h // 2

                # Draw bounding box and center point
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

                # Send the appropriate movement command to the EV3
                if area > AREA_CLOSE_THRESHOLD:
                    send_command("stop")  # Stop if the ball is close
                else:
                    left_boundary = frame_width * LEFT_BOUND_RATIO
                    right_boundary = frame_width * RIGHT_BOUND_RATIO

                    if cx < left_boundary:
                        send_command("left")  # Turn left if the ball is on the left
                    elif cx > right_boundary:
                        send_command("right")  # Turn right if the ball is on the right
                    else:
                        send_command("forward")  # Move forward if the ball is centered

        else:
            send_command("stop")  # No ball detected, stop moving

        # Show the current frame and mask
        cv2.imshow('Frame', frame)
        cv2.imshow('Mask', mask)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(LOOP_DELAY)

    cap.release()
    cv2.destroyAllWindows()
    send_command("stop")  # Stop the robot after the loop ends
    print("Exiting script.")

if __name__ == "__main__":
    main()
