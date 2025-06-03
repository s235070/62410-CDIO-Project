import cv2
import numpy as np
import math

MIN_RADIUS = 3
MAX_RADIUS = 25
CIRCULARITY_THRESHOLD = 0.7
kernel = np.ones((7, 7), np.uint8)

orange_lower = np.array([5, 140, 140])
orange_upper = np.array([18, 255, 255])
white_lower = np.array([0, 0, 200])
white_upper = np.array([180, 60, 255])
yellow_lower = np.array([20, 100, 100])
yellow_upper = np.array([35, 255, 255])

def detect_balls(frame, hsv_img, H, ev3_pos_arena, image_to_arena_coords):
    detected = []

    # White
    white_mask = cv2.inRange(hsv_img, white_lower, white_upper)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in white_contours:
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        if MIN_RADIUS < radius < MAX_RADIUS:
            arena_pos = image_to_arena_coords((int(x), int(y)), H)
            detected.append((arena_pos, "white", (int(x), int(y))))
            break

    # Orange
    orange_mask = cv2.inRange(hsv_img, orange_lower, orange_upper)
    orange_mask = cv2.morphologyEx(orange_mask, cv2.MORPH_OPEN, kernel)
    orange_mask = cv2.morphologyEx(orange_mask, cv2.MORPH_CLOSE, kernel)
    orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in orange_contours:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * (area / (perimeter ** 2))
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        if MIN_RADIUS < radius < MAX_RADIUS and circularity > CIRCULARITY_THRESHOLD:
            arena_pos = image_to_arena_coords((int(x), int(y)), H)
            detected.append((arena_pos, "orange", (int(x), int(y))))

    # Yellow
    yellow_mask = cv2.inRange(hsv_img, yellow_lower, yellow_upper)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)
    yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in yellow_contours:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * (area / (perimeter ** 2))
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        if MIN_RADIUS < radius < MAX_RADIUS and circularity > CIRCULARITY_THRESHOLD:
            arena_pos = image_to_arena_coords((int(x), int(y)), H)
            detected.append((arena_pos, "yellow", (int(x), int(y))))

    # Nearest
    nearest = None
    min_distance = float("inf")
    for arena_pos, color, screen_pos in detected:
        dx = arena_pos[0] - ev3_pos_arena[0]
        dy = arena_pos[1] - ev3_pos_arena[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist < min_distance:
            min_distance = dist
            nearest = (arena_pos, color, screen_pos)

    if nearest:
        arena_pos, color, screen_pos = nearest
        color_bgr = (255,255,255) if color=="white" else (0,165,255) if color=="orange" else (0,255,255)
        cv2.circle(frame, screen_pos, 10, color_bgr, 2)
        cv2.putText(frame, "{} ({:.2f},{:.2f})".format(color.title(), arena_pos[0], arena_pos[1]),
                    (screen_pos[0]+5, screen_pos[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_bgr, 1)
        return screen_pos, arena_pos
    else:
        return None
