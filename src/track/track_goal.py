# track/track_goal.py
import cv2
import numpy as np

# Arena-dimensioner i cm
ARENA_WIDTH_CM = 180
ARENA_HEIGHT_CM = 120

# Konverteringsfaktor fra cm til pixels (baseret på warp)
# Dette skal passe med WARP_WIDTH og WARP_HEIGHT i din config
WARP_WIDTH = 640
WARP_HEIGHT = 480
CM_TO_PX_X = WARP_WIDTH / ARENA_WIDTH_CM
CM_TO_PX_Y = WARP_HEIGHT / ARENA_HEIGHT_CM

def cm_to_px(x_cm, y_cm):
    """
    Konverterer koordinater fra cm til pixels i warp-billedet.
    """
    return int(x_cm * CM_TO_PX_X), int(y_cm * CM_TO_PX_Y)

def get_goal_positions():
    """
    Returnerer faste pixel-koordinater for mål A og mål B i det warpet billede.

    Returns:
        (goal_a_pos, goal_b_pos): Tuple med pixel-koordinater (x, y)
    """
    goal_a_cm = (5, 60)     # 5 cm fra venstre, midt i højden
    goal_b_cm = (175, 60)   # 5 cm fra højre, midt i højden

    goal_a_px = cm_to_px(*goal_a_cm)
    goal_b_px = cm_to_px(*goal_b_cm)

    return goal_a_px, goal_b_px

def draw_goals(image):
    """
    Tegner mål A og B på det warpet billede.

    Args:
        image: Warpet BGR-billede (f.eks. fra warp_image)

    Returns:
        Annoteret billede
    """
    img = image.copy()
    goal_a, goal_b = get_goal_positions()

    cv2.circle(img, goal_a, 10, (255, 100, 100), 2)
    cv2.putText(img, "Goal A", (goal_a[0] + 10, goal_a[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 1)

    cv2.circle(img, goal_b, 10, (100, 255, 100), 2)
    cv2.putText(img, "Goal B", (goal_b[0] + 10, goal_b[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)

    return img
