# pickup_ball.py
from ev3_control import send_command

def open_claw():
    send_command("python3 move_robot.py open_claw")
    print("[CLAW] Åbner kløerne...")

def close_claw():
    send_command("python3 move_robot.py close_claw")
    print("[CLAW] Lukker kløerne...")

def push_ball():
    send_command("python3 move_robot.py push_ball")
    print("[PUSHER] Skubber bolden...")

def slow_forward():
    send_command("python3 move_robot.py slow_forward")
    print("[MOVE] Kører langsomt frem...")

def pick_up_sequence():
    print("[SEKVENS] Starter boldopsamling...")
    open_claw()
    slow_forward()
    close_claw()
    print("[SEKVENS] Bold samlet.")
