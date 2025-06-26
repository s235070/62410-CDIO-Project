import cv2
import numpy as np
from config import WARP_WIDTH, WARP_HEIGHT

def create_wall_mask(warped_img, border_margin=15):
    h, w = warped_img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Define interior rectangle with safety margin
    inner_rect = np.array([
        [border_margin, border_margin],
        [w - border_margin, border_margin],
        [w - border_margin, h - border_margin],
        [border_margin, h - border_margin]
    ])
    
    cv2.fillPoly(mask, [inner_rect], 255)
    return mask

def get_wall_contour(warped_img):
    h, w = warped_img.shape[:2]
    return np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.int32)

def draw_arena_outline(warped_img):
    img = warped_img.copy()
    contour = get_wall_contour(warped_img)
    
    # Draw purple border
    cv2.polylines(img, [contour], True, (180, 0, 180), 2)
    
    # Draw corner markers
    for pt in contour:
        cv2.circle(img, tuple(pt), 6, (0, 0, 0), -1)
    
    return img

def create_arena_mask(border_margin=15):
    mask = np.zeros((WARP_HEIGHT, WARP_WIDTH), dtype=np.uint8)

    # Indre rektangel definerer spilleområdet, lidt inde fra kanten
    cv2.rectangle(
        mask,
        (border_margin, border_margin),
        (WARP_WIDTH - border_margin, WARP_HEIGHT - border_margin),
        255,
        -1
    )

    return mask