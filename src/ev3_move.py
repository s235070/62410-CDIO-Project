# ev3_move.py

import numpy as np
import time
from ev3_control import (
    send_safe_command,
    CMD_FORWARD,
    CMD_SPIN_LEFT,
    CMD_SPIN_RIGHT,
    CMD_BACK_A_LITTLE,
    CMD_STOP
)

last_cmd = None
command_cooldown = 0
CMD_DELAY_FRAMES = 2
has_stopped = False

# Justerbar afstand til mål/bold
STOP_DISTANCE = 120  # pixels

def move_towards_target(front, back, target, stop_distance=50):
    global last_cmd, command_cooldown

    if not front or not back:
        return False

    ev3_center = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)
    vx, vy = front[0] - back[0], front[1] - back[1]
    ux, uy = target[0] - front[0], target[1] - front[1]

    dot = vx * ux + vy * uy
    det = vx * uy - vy * ux
    angle = np.degrees(np.arctan2(det, dot))
    dist = np.hypot(target[0] - ev3_center[0], target[1] - ev3_center[1])

    if dist < stop_distance:
        if last_cmd != CMD_STOP:
            print(f"[GOAL-STOP] Tæt nok på mål (dist={dist:.1f}) → {CMD_STOP}")
            send_safe_command(CMD_STOP)
            last_cmd = CMD_STOP
        return True

    if abs(angle) > 10:
        cmd = CMD_SPIN_RIGHT if angle > 0 else CMD_SPIN_LEFT
    else:
        cmd = CMD_FORWARD

    if cmd != last_cmd or command_cooldown == 0:
        print(f"[GOAL-MOVE] angle={angle:.1f}, dist={dist:.1f} → {cmd}")
        send_safe_command(cmd)
        last_cmd = cmd
        command_cooldown = CMD_DELAY_FRAMES
    else:
        command_cooldown = max(0, command_cooldown - 1)

    return False

def go_to_goal(goal_pos, front, back):
    print("[GOAL] Kører mod mål...")
    while True:
        reached = move_towards_target(front, back, goal_pos, stop_distance=50)
        if reached:
            print("[GOAL] Ankommet til mål.")
            break
        time.sleep(0.1)

def reset_stop_state():
    global has_stopped
    has_stopped = False

def move_towards_ball(front, back, balls):
    global last_cmd, command_cooldown, has_stopped

    if not front or not back or not balls or has_stopped:
        return True

    ev3_center = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)
    vx, vy = front[0] - back[0], front[1] - back[1]

    nearest = None
    min_dist = float("inf")
    for _, (bx, by) in balls:
        d = np.hypot(back[0] - bx, back[1] - by)
        if d < 50:
            continue
        if d < min_dist:
            min_dist = d
            nearest = (bx, by)

    if nearest is None:
        return False

    ux, uy = nearest[0] - front[0], nearest[1] - front[1]
    dot = vx * ux + vy * uy
    det = vx * uy - vy * ux
    angle = np.degrees(np.arctan2(det, dot))

    if min_dist < STOP_DISTANCE:
        if last_cmd != CMD_STOP:
            print(f"[STOP] Stopper før bolden (dist={min_dist:.1f}) → {CMD_STOP}")
            send_safe_command(CMD_STOP)
            last_cmd = CMD_STOP
            has_stopped = True
        return True

    if abs(angle) > 10:
        cmd = CMD_SPIN_RIGHT if angle > 0 else CMD_SPIN_LEFT
    else:
        cmd = CMD_FORWARD

    if cmd != last_cmd or command_cooldown == 0:
        print(f"[MOVE] angle={angle:.1f}, dist={min_dist:.1f} → {cmd}")
        send_safe_command(cmd)
        last_cmd = cmd
        command_cooldown = CMD_DELAY_FRAMES
    else:
        command_cooldown = max(0, command_cooldown - 1)

    return False

def stop_ev3():
    global last_cmd, has_stopped
    send_safe_command(CMD_STOP)
    last_cmd = CMD_STOP
    has_stopped = True
    print("[FORCE STOP] Robotten blev tvunget til at stoppe")
