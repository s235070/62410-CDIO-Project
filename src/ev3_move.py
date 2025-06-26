# ev3_move.py

import numpy as np                  # For vector calculations (e.g., angle, distance)
import time                         # For delays and sleep
from ev3_control import (           # Import EV3 movement commands and command sender
    send_safe_command,
    CMD_FORWARD,
    CMD_SPIN_LEFT,
    CMD_SPIN_RIGHT,
    CMD_BACK_A_LITTLE,
    CMD_STOP
)

# Global state variables
last_cmd = None                     # Last command sent to avoid redundant commands
command_cooldown = 0               # Cooldown to avoid sending commands too frequently
CMD_DELAY_FRAMES = 2              # Frames to wait before allowing same command again
has_stopped = False               # Flag indicating if robot has stopped

# Adjustable threshold distance for stopping (in pixels)
STOP_DISTANCE = 100

def move_towards_target(front, back, target, stop_distance=50):
    """
    Move the robot toward a specific target (e.g., goal or waypoint).
    Uses vector math to align and drive the robot.
    Returns True if target is reached.
    """
    global last_cmd, command_cooldown

    # If robot markers not detected, exit early
    if not front or not back:
        return False

    # Calculate robot's center and orientation vector (front - back)
    ev3_center = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)
    vx, vy = front[0] - back[0], front[1] - back[1]
    
    # Vector from front of robot to target
    ux, uy = target[0] - front[0], target[1] - front[1]

    # Calculate angle between robot direction and target vector
    dot = vx * ux + vy * uy
    det = vx * uy - vy * ux
    angle = np.degrees(np.arctan2(det, dot))

    # Distance from robot center to target
    dist = np.hypot(target[0] - ev3_center[0], target[1] - ev3_center[1])

    # Stop if close enough to target
    if dist < stop_distance:
        if last_cmd != CMD_STOP:
            print(f"[GOAL-STOP] Tæt nok på mål (dist={dist:.1f}) → {CMD_STOP}")
            send_safe_command(CMD_STOP)
            last_cmd = CMD_STOP
        return True

    # Decide whether to turn or move forward based on angle
    if abs(angle) > 10:
        cmd = CMD_SPIN_RIGHT if angle > 0 else CMD_SPIN_LEFT
    else:
        cmd = CMD_FORWARD

    # Only send command if different from last or cooldown has expired
    if cmd != last_cmd or command_cooldown == 0:
        print(f"[GOAL-MOVE] angle={angle:.1f}, dist={dist:.1f} → {cmd}")
        send_safe_command(cmd)
        last_cmd = cmd
        command_cooldown = CMD_DELAY_FRAMES
    else:
        command_cooldown = max(0, command_cooldown - 1)

    return False

def go_to_goal(goal_pos, front, back):
    """
    High-level routine to move to a goal until reached.
    """
    print("[GOAL] Kører mod mål...")
    while True:
        reached = move_towards_target(front, back, goal_pos, stop_distance=50)
        if reached:
            print("[GOAL] Ankommet til mål.")
            break
        time.sleep(0.1)

def reset_stop_state():
    """
    Resets stop flag so robot can resume moving.
    """
    global has_stopped
    has_stopped = False

def move_towards_ball(front, back, balls):
    """
    Move the robot towards the nearest visible ball.
    Returns True if robot has stopped near a ball.
    """
    global last_cmd, command_cooldown, has_stopped

    # Exit early if data is missing or robot already stopped
    if not front or not back or not balls or has_stopped:
        return True

    # Calculate robot center and direction vector
    ev3_center = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)
    vx, vy = front[0] - back[0], front[1] - back[1]

    # Find nearest ball (excluding very close ones)
    nearest = None
    min_dist = float("inf")
    for _, (bx, by) in balls:
        d = np.hypot(back[0] - bx, back[1] - by)
        if d < 40:  # Ignore if too close (to avoid jitter or error)
            continue
        if d < min_dist:
            min_dist = d
            nearest = (bx, by)

    # If no valid ball found, exit
    if nearest is None:
        return False

    # Calculate vector and angle to ball
    ux, uy = nearest[0] - front[0], nearest[1] - front[1]
    dot = vx * ux + vy * uy
    det = vx * uy - vy * ux
    angle = np.degrees(np.arctan2(det, dot))

    # If close enough, stop
    if min_dist < STOP_DISTANCE:
        if last_cmd != CMD_STOP:
            print(f"[STOP] Stopper før bolden (dist={min_dist:.1f}) → {CMD_STOP}")
            send_safe_command(CMD_STOP)
            last_cmd = CMD_STOP
            has_stopped = True
        return True

    # Decide to turn or move forward
    if abs(angle) > 10:
        cmd = CMD_SPIN_RIGHT if angle > 0 else CMD_SPIN_LEFT
    else:
        cmd = CMD_FORWARD

    # Send command if needed
    if cmd != last_cmd or command_cooldown == 0:
        print(f"[MOVE] angle={angle:.1f}, dist={min_dist:.1f} → {cmd}")
        send_safe_command(cmd)
        last_cmd = cmd
        command_cooldown = CMD_DELAY_FRAMES
    else:
        command_cooldown = max(0, command_cooldown - 1)

    return False

def stop_ev3():
    """
    Forces the EV3 to stop and sets the stopped flag.
    """
    global last_cmd, has_stopped
    send_safe_command(CMD_STOP)
    last_cmd = CMD_STOP
    has_stopped = True
    print("[FORCE STOP] Robotten blev tvunget til at stoppe")
