import cv2
import numpy as np

def detect_long_wall_once(hsv_img, lower, upper):
    mask = cv2.inRange(hsv_img, lower, upper)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cnt for cnt in contours if cv2.contourArea(cnt) > 3000]

def get_extreme_corners(contour):
    contour = contour.reshape(-1, 2)
    return [
        tuple(min(contour, key=lambda p: p[0] + p[1])),
        tuple(max(contour, key=lambda p: p[0] - p[1])),
        tuple(max(contour, key=lambda p: p[0] + p[1])),
        tuple(max(contour, key=lambda p: p[1] - p[0])),
    ]

def compute_homography(corners):
    arena_coords = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], dtype=np.float32)
    return cv2.findHomography(np.array(corners, dtype=np.float32), arena_coords)[0]

def image_to_arena_coords(pt, H):
    pt_h = np.array([pt[0], pt[1], 1], dtype=np.float32).reshape(3, 1)
    arena_pt_h = H @ pt_h
    arena_pt_h /= arena_pt_h[2]
    return (arena_pt_h[0][0], arena_pt_h[1][0])

def arena_to_image(pt, H):
    pt = np.array([[pt]], dtype=np.float32)
    img_pt = cv2.perspectiveTransform(pt, np.linalg.inv(H))
    return tuple(map(int, img_pt[0][0]))

def draw_wall_and_grid(frame, contours, H):
    for cnt in contours:
        cv2.drawContours(frame, [cnt], -1, (0, 140, 255), 3)
        corners = get_extreme_corners(cnt)
        for i, corner in enumerate(corners):
            cv2.circle(frame, corner, 8, (0, 255, 255), -1)
            cv2.putText(frame, "C{}".format(i+1), (corner[0] + 10, corner[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        center_px = np.mean(np.array(corners), axis=0).astype(int)
        cv2.circle(frame, tuple(center_px), 6, (255, 255, 0), -1)
        cv2.putText(frame, "(0,0)", (center_px[0] + 10, center_px[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        for x in np.arange(-1, 1.01, 0.2):
            for y in np.arange(-1, 1.01, 0.2):
                img_pt = arena_to_image((x, y), H)
                cv2.circle(frame, img_pt, 2, (150, 255, 150), -1)
                if abs(x) < 0.01 and abs(y) < 0.01:
                    continue
                cv2.putText(frame, "({:.1f},{:.1f})".format(x, y), (img_pt[0]+5, img_pt[1]-5),
                            cv2.FONT_HERSHEY_PLAIN, 0.7, (180, 255, 180), 1)
