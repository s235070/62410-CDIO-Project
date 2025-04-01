#!/usr/bin/env python3
import sys, tty, termios
from ev3dev2.motor import LargeMotor, OUTPUT_C

motor = LargeMotor(OUTPUT_C)
SPEED = 50
DURATION = 1  # seconds motor should run per press

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

print("Tryk F (frem), B (baglæns), X for exit.")

while True:
    key = get_key().lower()

    if key == 'f':
        print("Frem")
        motor.on_for_seconds(SPEED, DURATION, brake=True, block=True)
    elif key == 'b':
        print("Baglæns")
        motor.on_for_seconds(-SPEED, DURATION, brake=True, block=True)
    elif key == 'x':
        print("Farvel")
        break

