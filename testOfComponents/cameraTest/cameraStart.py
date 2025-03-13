import cv2

def main():
    cap = cv2.VideoCapture(1)  # Use device index 1 for USB camera

    if not cap.isOpened():
        print("Cannot open camera on index 1.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Exiting...")
            break

        cv2.imshow('USB Camera Feed', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
