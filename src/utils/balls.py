# src/utils/balls.py

import cv2
import numpy as np

def detect_color_ball(frame, hsv_img, lower, upper, color_name, WARP_WIDTH, WARP_HEIGHT):
    mask = cv2.inRange(hsv_img, lower, upper)

    # ROI: symmetric 20px margin all around
    margin = 20
    roi_mask = np.zeros_like(mask)
    cv2.rectangle(roi_mask, (margin, margin), (WARP_WIDTH - margin, WARP_HEIGHT - margin), 255, -1)
    mask = cv2.bitwise_and(mask, roi_mask)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ball_centers = []

    for cnt in contours:
        (x, y), radius = cv2.minEnclosingCircle(cnt)

        # Basic radius check
        if radius > 3:
            # Example: filtering large white EV3 parts
            if color_name == "White" and radius > 15:
                continue

            center = (int(x), int(y))
            ball_centers.append(center)

            # Draw for debug
            cv2.circle(frame, center, int(radius), (0, 255, 0), 2)
            cv2.putText(frame, color_name, (center[0] + 5, center[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return ball_centers