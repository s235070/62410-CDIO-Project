import cv2
import numpy as np
import time
import os

from config import CAMERA_INDEX, WARP_WIDTH, WARP_HEIGHT
from utils.vision import warp_image

from track.input_handler import ask_for_label, load_matrix, load_wall_profiles
from track.track_ev3 import detect_ev3
from track.track_balls import detect_balls
from track.track_wall import (
    detect_long_wall_once,
    get_extreme_corners,
    compute_homography,
    image_to_arena_coords,
    arena_to_image,
    draw_wall_and_grid
    
)

def main():
    os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "1"

    # Load user settings
    label = ask_for_label()
    matrix = load_matrix(label)
    if matrix is None:
        return

    wall_profiles = load_wall_profiles()
    if wall_profiles is None:
        return

    # Init camera
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WARP_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WARP_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)

    # Detect wall and compute homography
    print("[INFO] Detecting wall...")
    H = None
    wall_contours = []

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

        for name, profile in wall_profiles.items():
            lower = np.array(profile["lower"])
            upper = np.array(profile["upper"])
            contours = detect_long_wall_once(hsv, lower, upper)
            if contours:
                wall_contours = contours
                corners = get_extreme_corners(contours[0])
                H = compute_homography(corners)
                print("[INFO] Wall detected using profile:", name)
                break
        if H is not None:
            break

    # Start main loop
    print("[INFO] Starting main loop...")
    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            continue

        warped = warp_image(frame, matrix, WARP_WIDTH, WARP_HEIGHT)
        hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

        draw_wall_and_grid(warped, wall_contours, H)

        robot_front, robot_back = detect_ev3(warped)
        if robot_front and robot_back:
            ev3_pos = robot_back
            ev3_front = robot_front
            ev3_pos_arena = image_to_arena_coords(ev3_pos, H)
            ev3_front_arena = image_to_arena_coords(ev3_front, H)
        

            # 🔎 Find og tegn alle bolde
            all_balls, nearest = detect_balls(
                warped, hsv, H, ev3_pos_arena, image_to_arena_coords
            )

            

            for arena_pos, color, screen_pos in all_balls:
                color_bgr = (255, 255, 255) if color == "white" else (0, 165, 255) if color == "orange" else (0, 255, 255)
                cv2.circle(warped, screen_pos, 8, color_bgr, 2)
                cv2.putText(
                    warped,
                    f"{color.title()} ({arena_pos[0]:.2f},{arena_pos[1]:.2f})",
                    (screen_pos[0] + 5, screen_pos[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color_bgr,
                    1
                )

            # 🟡 Tegn pil til nærmeste bold
            if nearest:
                arena_pos, color, screen_pos = nearest
                dx = arena_pos[0] - ev3_pos_arena[0]
                dy = arena_pos[1] - ev3_pos_arena[1]
                target_vec = np.array([dx, dy])
                front_vec = np.array(ev3_front_arena) - np.array(ev3_pos_arena)

                angle = np.degrees(np.arctan2(
                    np.cross(front_vec, target_vec),
                    np.dot(front_vec, target_vec)
                ))
                distance = np.linalg.norm(target_vec)

                cv2.arrowedLine(warped, robot_front, screen_pos, (0, 255, 255), 2)

            # 🟢 Tegn EV3 robot
            cv2.circle(warped, robot_front, 8, (0, 255, 0), -1)
            cv2.circle(warped, robot_back, 8, (255, 255, 0), -1)
            cv2.putText(warped, "EV3", (robot_front[0] + 10, robot_front[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # FPS visning
        fps = 1.0 / (time.time() - start_time)
        cv2.putText(warped, f"FPS: {fps:.1f}", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imshow("EV3 Tracking", warped)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()