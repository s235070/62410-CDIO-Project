import cv2
import numpy as np
import subprocess

def main():
    # Open your USB camera (likely index 1)
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Cannot open camera on index 1.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Exiting...")
            break

        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define HSV range for orange (adjust if needed)
        lower_orange = np.array([10, 100, 100])
        upper_orange = np.array([25, 255, 255])

        # Make a mask
        mask = cv2.inRange(hsv, lower_orange, upper_orange)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Largest contour by area
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if area > 100:  # Ignore tiny specks
                x, y, w, h = cv2.boundingRect(largest_contour)
                # Draw bounding box around the ball
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Also draw a center point
                cx = x + w//2
                cy = y + h//2
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

                # Prepare the command to send to EV3
                EV3_USER = 'robot'  # Adjust to your user on EV3
                EV3_IP = '172.20.10.8'  # Adjust to your EV3's IP address
                command = f"Move to {cx}, {cy}"  # You can define a command or more logic here
                
                # Send the command to EV3 via SSH (use subprocess)
                full_command = f'ssh {EV3_USER}@{EV3_IP} "python3 -c \'{command}\'"'
                try:
                    subprocess.run(full_command, shell=True, check=True)
                    print(f"Command sent: {command}")
                except subprocess.CalledProcessError as e:
                    print(f"Error sending command to EV3: {e}")

        # Show both frames
        cv2.imshow('Original + Detection', frame)
        cv2.imshow('Mask', mask)

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
