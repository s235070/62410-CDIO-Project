import cv2
import numpy as np
from config import CAMERA_INDEX, PROFILE_DIR, WARP_WIDTH, WARP_HEIGHT
from utils.vision import warp_image

def nothing(x):
    pass

def main():
    label = input("Enter saved scenario label (e.g. dim): ").strip().lower()
    matrix_path = PROFILE_DIR / f"{label}_matrix.npy"
    if not matrix_path.exists():
        print(f"[ERROR] Matrix not found: {matrix_path}")
        return

    matrix = np.load(matrix_path)
    cap = cv2.VideoCapture(CAMERA_INDEX)

    # Create HSV trackbars
    cv2.namedWindow("HSV Sliders")
    cv2.createTrackbar("H_min", "HSV Sliders", 0, 180, nothing)
    cv2.createTrackbar("H_max", "HSV Sliders", 180, 180, nothing)
    cv2.createTrackbar("S_min", "HSV Sliders", 0, 255, nothing)
    cv2.createTrackbar("S_max", "HSV Sliders", 255, 255, nothing)
    cv2.createTrackbar("V_min", "HSV Sliders", 0, 255, nothing)
    cv2.createTrackbar("V_max", "HSV Sliders", 255, 255, nothing)

    print("[INFO] Press 'q' to quit and print HSV values.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

        # Get current HSV values
        h_min = cv2.getTrackbarPos("H_min", "HSV Sliders")
        h_max = cv2.getTrackbarPos("H_max", "HSV Sliders")
        s_min = cv2.getTrackbarPos("S_min", "HSV Sliders")
        s_max = cv2.getTrackbarPos("S_max", "HSV Sliders")
        v_min = cv2.getTrackbarPos("V_min", "HSV Sliders")
        v_max = cv2.getTrackbarPos("V_max", "HSV Sliders")

        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])

        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(warped, warped, mask=mask)

        cv2.imshow("Warped Arena", warped)
        cv2.imshow("Color Mask", result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"\n[HSV Range]")
    print(f"Lower: {lower}")
    print(f"Upper: {upper}")

if __name__ == "__main__":
    main()