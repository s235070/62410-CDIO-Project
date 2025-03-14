import cv2
import numpy as np
import subprocess

def send_ev3_command(cmd):
    # Adjust <EV3_IP> or ev3dev.local to your actual EV3 address
    subprocess.run([
        "ssh", "robot@<EV3_IP>",
        "python3", "/home/robot/move_robot.py", cmd
    ])

def main():
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Cannot open camera index 1")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_orange = np.array([10, 100, 100])
        upper_orange = np.array([25, 255, 255])
        mask = cv2.inRange(hsv, lower_orange, upper_orange)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)

            if area > 100:
                x, y, w, h = cv2.boundingRect(largest)
                cx = x + w//2
                cy = y + h//2
                # Draw
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
                cv2.circle(frame, (cx, cy), 5, (255,0,0), -1)

                # Robot logic
                # 1) If the area is big, stop
                if area > 2000:
                    send_ev3_command("stop")
                else:
                    # Decide if ball is left, right, or center
                    left_boundary = frame_width * 0.4
                    right_boundary = frame_width * 0.6
                    if cx < left_boundary:
                        send_ev3_command("left")
                    elif cx > right_boundary:
                        send_ev3_command("right")
                    else:
                        send_ev3_command("forward")

        else:
            # If no contour found, maybe stop or keep turning?
            send_ev3_command("stop")

        cv2.imshow('frame', frame)
        cv2.imshow('mask', mask)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    # On exit, stop the robot
    send_ev3_command("stop")

if __name__ == "__main__":
    main()
