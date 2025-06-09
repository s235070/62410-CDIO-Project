import cv2
import numpy as np

def select_detection_zone(image):
    """
    Lader brugeren klikke 4 punkter i billedet for at definere detektionszonen (clockwise).
    Returnerer et polygon som np.array med (4, 2)
    """
    points = []

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            points.append((x, y))
            print(f"[INFO] Point {len(points)}: ({x}, {y})")

    clone = image.copy()
    cv2.imshow("Select 4 detection zone corners", clone)
    cv2.setMouseCallback("Select 4 detection zone corners", mouse_callback)

    while len(points) < 4:
        cv2.waitKey(1)

    cv2.destroyWindow("Select 4 detection zone corners")
    return np.array(points, dtype=np.int32)


def create_manual_mask(polygon, shape):
    """
    Opretter en binær maske med polygonens område sat til 255 og resten 0.

    Args:
        polygon: np.array med 4 (x, y)-punkter
        shape: ønsket maskestørrelse (h, w)

    Returns:
        mask: uint8 binær maske
    """
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(mask, [polygon], 255)
    return mask
