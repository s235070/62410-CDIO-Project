import cv2
import numpy as np
import math

# === HSV farveområder for hver boldtype ===
COLOR_RANGES = {
    "white":  (np.array([0, 0, 200]),   np.array([180, 60, 255])),
    "orange": (np.array([5, 140, 140]), np.array([18, 255, 255])),
    "yellow": (np.array([20, 100, 100]), np.array([35, 255, 255]))
}

# === Detektionsparametre ===
MIN_RADIUS = 3
MAX_RADIUS = 25
CIRCULARITY_THRESHOLD = 0.7
KERNEL = np.ones((5, 5), np.uint8)

def apply_mask_and_filter(hsv_img, lower, upper, wall_mask):
    """
    Opretter en HSV-maske og anvender vægmasken for at ignorere vægområder.
    """
    mask = cv2.inRange(hsv_img, lower, upper)
    mask = cv2.bitwise_and(mask, wall_mask)  # fjern væggen
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL)
    return mask

def check_valid_ball(cnt):
    """
    Tjekker om kontur matcher krav til radius og cirkularitet.
    """
    (x, y), radius = cv2.minEnclosingCircle(cnt)
    if not (MIN_RADIUS < radius < MAX_RADIUS):
        return None
    
    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)
    if perimeter == 0:
        return None
    circularity = 4 * np.pi * area / (perimeter ** 2)
    if circularity < CIRCULARITY_THRESHOLD:
        return None
    
    return (int(x), int(y)), radius

def detect_balls(warped_img, hsv_img, wall_mask):
    """
    Detekterer bolde baseret på HSV, filtrerer væg, returnerer liste over fundne bolde.
    """
    detected = []

    for color_name, (lower, upper) in COLOR_RANGES.items():
        mask = apply_mask_and_filter(hsv_img, lower, upper, wall_mask)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 🔍 DEBUG: vis HSV-masken for denne farve
        cv2.imshow(f"{color_name.title()} Mask", mask)

        for cnt in contours:
            result = check_valid_ball(cnt)
            if result is None:
                continue
            (x, y), _ = result

            # Omregn til arena-koordinater (top-down) – her returneres kun skærmkoord.
            # Hvis du senere bruger homografi, kan du transformere (x, y)
            detected.append(((None, None), color_name, (x, y)))  # Arena-pos = None for nu

    return detected