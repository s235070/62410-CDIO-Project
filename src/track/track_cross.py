import cv2
import numpy as np
from config import PROFILE_DIR


def load_cross_polygon(label):
    """
    Loader en gemt .npy-fil med polygonkoordinater for korset
    """
    path = PROFILE_DIR / f"{label}_cross.npy"
    if path.exists():
        try:
            poly = np.load(path)
            if poly.shape == (4, 2):
                return poly
            else:
                print(f"[ERROR] Invalid shape for cross polygon: {poly.shape}")
        except Exception as e:
            print(f"[ERROR] Could not load cross polygon: {e}")
    return None






def detect_cross_region(warped_img):
    """
    Detects the red cross on the arena using HSV color segmentation,
    morphological filtering, and contour analysis.

    Args:
        warped_img: The top-down warped image from homography (BGR image)

    Returns:
        A polygon (Nx2 numpy array) representing the contour of the detected cross,
        or None if no suitable region was found.
    """
    hsv = cv2.cvtColor(warped_img, cv2.COLOR_BGR2HSV)

    # Red in HSV (handle wraparound)
    lower_red1 = np.array([0, 90, 90])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 90, 90])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    best_candidate = None
    best_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 3000 or area > 25000:
            continue

        approx = cv2.approxPolyDP(cnt, epsilon=10, closed=True)
        if len(approx) < 4:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        ratio = w / h
        if 0.75 < ratio < 1.3 and area > best_area:
            best_candidate = approx.reshape(-1, 2)
            best_area = area

    if best_candidate is not None:
        return best_candidate

    return None
