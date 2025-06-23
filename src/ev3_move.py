# ev3_move.py
import numpy as np
from ev3_control import send_command

CMD_FORWARD = "python3 move_robot.py forward"
CMD_SPIN_LEFT = "python3 move_robot.py spin_left"
CMD_SPIN_RIGHT = "python3 move_robot.py spin_right"
CMD_STOP = "python3 move_robot.py stop"

last_cmd = None
command_cooldown = 0
CMD_DELAY_FRAMES = 2
has_stopped = False  # ← vigtigt: stopper ALT bagefter

# Du kan justere denne værdi:
STOP_DISTANCE = 140  # afstand i pixels til bolden, hvor vi stopper

def move_towards_ball(front, back, balls):
    global last_cmd, command_cooldown, has_stopped

    if not front or not back or not balls or has_stopped:
        return True  # Hvis vi allerede har stoppet → afslut

    # Robotens center = midt mellem front og bag
    ev3_center = ((front[0] + back[0]) // 2, (front[1] + back[1]) // 2)
    vx, vy = front[0] - back[0], front[1] - back[1]

    # Find nærmeste bold
    nearest = None
    min_dist = float("inf")
    for _, (bx, by) in balls:
        d = np.hypot(back[0] - bx, back[1] - by)  # afstand fra bagenden
        if d < 60:
            continue
        if d < min_dist:
            min_dist = d
            nearest = (bx, by)

    if nearest is None:
        return False

    # Bold-retning ift. EV3
    ux, uy = nearest[0] - front[0], nearest[1] - front[1]
    dot = vx * ux + vy * uy
    det = vx * uy - vy * ux
    angle = np.degrees(np.arctan2(det, dot))

    # === STOPPUNKT ===
    if min_dist < STOP_DISTANCE:
        if last_cmd != CMD_STOP:
            print(f"[STOP] Stopper før bolden (dist={min_dist:.1f}) → {CMD_STOP}")
            send_command(CMD_STOP)
            last_cmd = CMD_STOP
            has_stopped = True
        return True  # Vi har nået destination

    # === Drej eller kør frem ===
    if abs(angle) > 10:
        cmd = CMD_SPIN_RIGHT if angle > 0 else CMD_SPIN_LEFT
    else:
        cmd = CMD_FORWARD

    if cmd != last_cmd or command_cooldown == 0:
        print(f"[MOVE] angle={angle:.1f}, dist={min_dist:.1f} → {cmd}")
        send_command(cmd)
        last_cmd = cmd
        command_cooldown = CMD_DELAY_FRAMES
    else:
        command_cooldown = max(0, command_cooldown - 1)

    return False  # Vi har ikke ramt bolden endnu

def stop_ev3():
    global last_cmd, has_stopped
    send_command(CMD_STOP)
    last_cmd = CMD_STOP
    has_stopped = True
    print("[FORCE STOP] Robotten blev tvunget til at stoppe")
