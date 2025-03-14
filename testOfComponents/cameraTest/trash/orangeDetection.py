#!/usr/bin/env python3

import cv2
import numpy as np

def main():
    # Adjust the device index to your USB camera
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Cannot open camera on index 1.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Exiting...")
            break

        # Convert the frame from BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define lower and upper bounds for "orange" in HSV
        # These are approximate and you may tweak them.
        lower_orange = np.array([10, 100, 100])
        upper_orange = np.array([25, 255, 255])

        # Create a binary mask where orange regions are white
        mask = cv2.inRange(hsv, lower_orange, upper_orange)

        # Show the original image
        cv2.imshow('Original', frame)

        # Show the mask (white where orange is detected)
        cv2.imshow('Orange Mask', mask)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
