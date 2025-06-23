# ev3_move.py
import numpy as np
import time
from ev3_control import send_command

CMD_FORWARD = "python3 move_robot.py forward"
CMD_SPIN_LEFT = "python3 move_robot.py spin_left"
CMD_SPIN_RIGHT = "python3 move_robot.py spin_right"
CMD_STOP = "python3 move_robot.py stop"

last_cmd = None
command_cooldown = 0
CMD_DELAY_FRAMES = 2  # Undgå spam

def move_towards_ball(front, back, balls):
    global last_cmd, command_cooldown

    if not front or not back or not balls:
        return

    ev3_center = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)

    # Beregn vektor
    vx, vy = front[0] - back[0], front[1] - back[1]

    # Find nærmeste bold
    nearest = None
    min_dist = float("inf")
    for _, (bx, by) in balls:
        d = np.hypot(back[0] - bx, back[1] - by)
        if d < 45:
            continue
        if d < min_dist:
            min_dist = d
            nearest = (bx, by)

    if nearest is None:
        return

    # Vinkelberegning
    ux, uy = nearest[0] - front[0], nearest[1] - front[1]
    dot = vx * ux + vy * uy
    det = vx * uy - vy * ux
    angle = np.degrees(np.arctan2(det, dot))

    # Bevægelsesvalg
    cmd = None
    if abs(angle) > 10:
        cmd = CMD_SPIN_RIGHT if angle > 0 else CMD_SPIN_LEFT
        print(f"[DREJ] angle={angle:.1f}° → {cmd}")
    else:
        if min_dist < 40:
            cmd = CMD_STOP
        else:
            cmd = CMD_FORWARD
        print(f"[KØR] dist={min_dist:.0f} → {cmd}")

    # Send kommando hvis den er ny eller cooldown er 0
    if cmd and (cmd != last_cmd or command_cooldown == 0):
        send_command(cmd)
        last_cmd = cmd
        command_cooldown = CMD_DELAY_FRAMES
    else:
        command_cooldown = max(0, command_cooldown - 1)
