import cv2
import numpy as np

def main():
    cap = cv2.VideoCapture(1)  # Adjust index if needed

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

        # Define HSV range for orange
        lower_orange = np.array([10, 100, 100])
        upper_orange = np.array([25, 255, 255])

        # Make a mask
        mask = cv2.inRange(hsv, lower_orange, upper_orange)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if area > 100:  # Filter out tiny noise
                x, y, w, h = cv2.boundingRect(largest_contour)
                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Center of bounding box
                cx = x + w//2
                cy = y + h//2

                # Draw center point
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

                # Print info to console
                print(f"Area={area:.1f}, Center=({cx}, {cy})")

        # Show visuals
        cv2.imshow('Detection', frame)
        cv2.imshow('Mask', mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
