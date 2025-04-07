import cv2
import numpy as np

def select_corners(image):
    """Let us click 4 corners in clockwise order."""
    points = []

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            print(f"[INFO] Point {len(points)}: ({x}, {y})")

    clone = image.copy()
    cv2.imshow("Select 4 arena corners (clockwise)", clone)
    cv2.setMouseCallback("Select 4 arena corners (clockwise)", mouse_callback)

    while len(points) < 4:
        cv2.waitKey(1)

    cv2.destroyAllWindows()
    return np.array(points, dtype=np.float32)

def compute_homography(src_pts, width, height):
    """Generate a homography matrix to warp to top-down view."""
    dst_pts = np.array([
        [0, 0],
        [width, 0],
        [width, height],
        [0, height]
    ], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    return matrix

def warp_image(image, matrix, width, height):
    """Warp the given image using the homography matrix."""
    warped = cv2.warpPerspective(image, matrix, (width, height))
    return warped
