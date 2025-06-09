import cv2
import numpy as np
from config import WARP_WIDTH, WARP_HEIGHT

def create_wall_mask(warped_img, border_margin=15):
    """
    Creates a binary mask where the playable area is white (255) and wall area is black (0)
    with a safety margin to ensure balls near walls are still detectable
    
    Args:
        warped_img: Warped top-down image from homography
        border_margin: Safety margin from arena edges (pixels)
    
    Returns:
        Binary mask (uint8 numpy array)
    """
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
    """
    Returns the 4-point contour representing the arena walls
    
    Args:
        warped_img: Warped top-down image
        
    Returns:
        Contour points (numpy array)
    """
    h, w = warped_img.shape[:2]
    return np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.int32)

def draw_arena_outline(warped_img):
    """
    Draws visual markers for arena walls on the warped image
    
    Args:
        warped_img: Warped top-down image
        
    Returns:
        Image with visual annotations
    """
    img = warped_img.copy()
    contour = get_wall_contour(warped_img)
    
    # Draw purple border
    cv2.polylines(img, [contour], True, (180, 0, 180), 2)
    
    # Draw corner markers
    for pt in contour:
        cv2.circle(img, tuple(pt), 6, (0, 0, 0), -1)
    
    return img

def create_arena_mask(border_margin=15):
    """
    Returnerer en binær maske (640x480), hvor kun indersiden af arenaen (med margin)
    er sat til 255, og alt andet (inkl. vægge) er sort (0).

    Args:
        border_margin: hvor meget afstand fra kanten vi skal holde os fra

    Returns:
        mask: binært billede med kun det indre område sat til 255
    """
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