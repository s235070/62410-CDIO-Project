import cv2
import numpy as np
import math

# Constants
MIN_RADIUS = 3
MAX_RADIUS = 25
CIRCULARITY_THRESHOLD = 0.75
ROBOT_AVOID_RADIUS = 40
IMAGE_EDGE_MARGIN = 12
ARENA_EDGE_MARGIN = 0.07

# Kernels
kernel7 = np.ones((7, 7), np.uint8)
kernel3 = np.ones((3, 3), np.uint8)

# Color rangesQ
COLOR_RANGES = {
    "white": (np.array([0, 0, 200]), np.array([180, 60, 255])),
    "orange": (np.array([5, 140, 140]), np.array([18, 255, 255])),
    "yellow": (np.array([20, 100, 100]), np.array([35, 255, 255]))
}

# Processing parameters
COLOR_CONFIG = {
    "white": {"open": kernel3, "close": None, "circularity": False},
    "orange": {"open": kernel7, "close": kernel7, "circularity": True},
    "yellow": {"open": kernel7, "close": None, "circularity": True}
}

def process_color(hsv_img, lower, upper, open_kernel, close_kernel):
    mask = cv2.inRange(hsv_img, lower, upper)
    if open_kernel is not None:
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_kernel)
    if close_kernel is not None:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel)
    return mask

def check_contour(cnt, use_circularity):
    (x, y), radius = cv2.minEnclosingCircle(cnt)
    if not (MIN_RADIUS < radius < MAX_RADIUS):
        return None
    
    if use_circularity:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0: 
            return None
        circularity = 4 * np.pi * area / (perimeter ** 2)
        if circularity < CIRCULARITY_THRESHOLD:
            return None
    return (int(x), int(y)), radius

def is_near_edge(x, y, frame, arena_pos):
    h, w = frame.shape[:2]
    return (x < IMAGE_EDGE_MARGIN or x > w - IMAGE_EDGE_MARGIN or
            y < IMAGE_EDGE_MARGIN or y > h - IMAGE_EDGE_MARGIN or
            abs(arena_pos[0]) > 1 - ARENA_EDGE_MARGIN or
            abs(arena_pos[1]) > 1 - ARENA_EDGE_MARGIN)

def detect_balls(frame, hsv_img, H, ev3_pos_arena, image_to_arena_coords, robot_front=None, robot_pos=None):
    detected = []
    masks = {}

    # Process all colors
    for color, (lower, upper) in COLOR_RANGES.items():
        cfg = COLOR_CONFIG[color]
        mask = process_color(hsv_img, lower, upper, cfg["open"], cfg["close"])
        
        # Mask robot areas
        for pos in [robot_front, robot_pos]:
            if pos is not None:
                cv2.circle(mask, pos, ROBOT_AVOID_RADIUS, 0, -1)
        
        masks[color] = mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            result = check_contour(cnt, cfg["circularity"])
            if result is None:
                continue
                
            (x, y), _ = result
            arena_pos = image_to_arena_coords((x, y), H)
            
            if is_near_edge(x, y, frame, arena_pos):
                continue
                
            detected.append((arena_pos, color, (x, y)))
    
    # Find nearest ball
    nearest = min(
        detected,
        key=lambda b: math.hypot(b[0][0] - ev3_pos_arena[0], b[0][1] - ev3_pos_arena[1]),
        default=None
    )
    
    return detected, nearest