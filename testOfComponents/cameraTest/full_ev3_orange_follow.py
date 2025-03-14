import cv2
import numpy as np
import subprocess
import time
import matplotlib.pyplot as plt

# CONFIGURATION
EV3_IP = "172.20.10.8"
REMOTE_SCRIPT = "/home/robot/62410-CDIO-Project/testOfComponents/cameraTest/move_robot.py"
CAMERA_INDEX = 1
LOWER_ORANGE = np.array([10, 100, 100])
UPPER_ORANGE = np.array([25, 255, 255])
AREA_CLOSE_THRESHOLD = 2000
LEFT_BOUND_RATIO = 0.4
RIGHT_BOUND_RATIO = 0.6
LOOP_DELAY = 0.1

def send_command(cmd):
    """Send commands to EV3 via SSH."""
    try:
        subprocess.run([
            "ssh", "robot@{}".format(EV3_IP),
            "python3", REMOTE_SCRIPT, cmd
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("Error sending command '{}' to EV3: {}".format(cmd, e))

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Cannot open camera at index {}".format(CAMERA_INDEX))
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    print("Starting camera loop. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera read failed.")
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)

            if area > 100:
                x, y, w, h = cv2.boundingRect(c)
                cx = x + w//2
                cy = y + h//2

                # Draw bounding box and center point
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                cv2.putText(frame, "Area:{}".format(area), (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

                # Decide movement command based on ball's area and position
                if area > AREA_CLOSE_THRESHOLD:
                    send_command("stop")
                else:
                    left_boundary = frame_width * LEFT_BOUND_RATIO
                    right_boundary = frame_width * RIGHT_BOUND_RATIO

                    if cx < left_boundary:
                        send_command("left")
                    elif cx > right_boundary:
                        send_command("right")
                    else:
                        send_command("forward")
            else:
                send_command("stop")
        else:
            send_command("stop")

        # Show frames using matplotlib (instead of cv2.imshow)
        plt.imshow(frame)
        plt.title("Frame")
        plt.axis("off")  # Hide axes
        plt.show()

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(LOOP_DELAY)

    cap.release()
    cv2.destroyAllWindows()
    send_command("stop")
    print("Exiting script.")

if __name__ == "__main__":
    main()
