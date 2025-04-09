import cv2
import numpy as np
from config import CAMERA_INDEX, PROFILE_DIR, WARP_WIDTH, WARP_HEIGHT
from utils.vision import warp_image

def detect_color_ball(frame, hsv_img, lower, upper, color_name):
    mask = cv2.inRange(hsv_img, lower, upper)

    # ROI: symmetric 30px margin all around
    margin = 15
    roi_mask = np.zeros_like(mask)
    cv2.rectangle(roi_mask, (margin, margin), (WARP_WIDTH - margin, WARP_HEIGHT - margin), 255, -1)
    mask = cv2.bitwise_and(mask, roi_mask)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ball_centers = []

    for cnt in contours:
        (x, y), radius = cv2.minEnclosingCircle(cnt)

        # Basic radius check
        if radius > 3:
            # White filter to suppress EV3
            if color_name == "White" and radius > 15:
                continue

            center = (int(x), int(y))
            ball_centers.append(center)

            cv2.circle(frame, center, int(radius), (0, 255, 0), 2)
            cv2.putText(frame, color_name, (center[0] + 5, center[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return ball_centers

def main():
    label = input("Enter saved scenario label (e.g. dim): ").strip().lower()
    matrix_path = PROFILE_DIR / f"{label}_matrix.npy"

    if not matrix_path.exists():
        print(f"[ERROR] Matrix not found: {matrix_path}")
        return

    matrix = np.load(matrix_path)
    cap = cv2.VideoCapture(CAMERA_INDEX)

    # HSV for orange ball
    orange_lower = np.array([10, 170, 190])
    orange_upper = np.array([26, 255, 255])

    # HSV for white ball
    white_lower = np.array([0, 5, 198])
    white_upper = np.array([180, 66, 255])

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

        detect_color_ball(warped, hsv, orange_lower, orange_upper, "Orange")
        detect_color_ball(warped, hsv, white_lower, white_upper, "White")

        cv2.imshow("Ball Detection (Warped)", warped)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()