import cv2
import numpy as np
from config import CAMERA_INDEX, PROFILE_DIR, WARP_WIDTH, WARP_HEIGHT
from utils.vision import warp_image

def main():
    label = input("Enter saved scenario label (e.g. dim): ").strip().lower()
    matrix_path = PROFILE_DIR / f"{label}_matrix.npy"
    if not matrix_path.exists():
        print(f"[ERROR] Matrix not found: {matrix_path}")
        return

    matrix = np.load(matrix_path)
    cap = cv2.VideoCapture(CAMERA_INDEX)

    # HSV ranges for ball colors
    white_lower = np.array([0, 5, 198])
    white_upper = np.array([180, 66, 255])
    orange_lower = np.array([10, 184, 204])
    orange_upper = np.array([26, 255, 255])

    margin_arena = 20

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

        # Ball masks
        white_mask = cv2.inRange(hsv, white_lower, white_upper)
        orange_mask = cv2.inRange(hsv, orange_lower, orange_upper)

        # Arena masking
        arena_mask = np.zeros_like(white_mask)
        cv2.rectangle(arena_mask, (margin_arena, margin_arena),
                      (WARP_WIDTH - margin_arena, WARP_HEIGHT - margin_arena), 255, -1)

        white_mask = cv2.bitwise_and(white_mask, arena_mask)
        orange_mask = cv2.bitwise_and(orange_mask, arena_mask)

        # Draw balls
        for mask, color_name, draw_color in [
            (white_mask, "White", (255, 255, 255)),
            (orange_mask, "Orange", (0, 165, 255))
        ]:
            cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts:
                (x, y), r = cv2.minEnclosingCircle(c)
                if 4 < r < 20:
                    center = (int(x), int(y))
                    cv2.circle(warped, center, 6, draw_color, 2)
                    cv2.putText(warped, color_name, (center[0] + 5, center[1] - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, draw_color, 1)

        cv2.imshow("Ball Detection Only", warped)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()