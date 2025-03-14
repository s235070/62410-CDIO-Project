import cv2
import numpy as np
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from time import sleep

# Initialize EV3 motors on ports B & C
tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)

# Open PC camera (change to 1 if needed)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame. Exiting...")
        break

    # Convert frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define orange color range (adjust if needed)
    lower_orange = np.array([10, 100, 100])
    upper_orange = np.array([25, 255, 255])

    # Create a mask
    mask = cv2.inRange(hsv, lower_orange, upper_orange)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        if area > 100:  # Only respond to significant objects
            print("Orange ball detected! Moving forward.")
            tank_drive.on(left_speed=30, right_speed=30)
        else:
            print("No ball detected. Stopping.")
            tank_drive.off()
    else:
        print("No ball detected. Stopping.")
        tank_drive.off()

    # Show camera feed (optional)
    cv2.imshow('Camera', frame)
    cv2.imshow('Mask', mask)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
tank_drive.off()
