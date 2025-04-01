#!/usr/bin/env python3
from ev3dev2.motor import MoveTank, OUTPUT_D, OUTPUT_A
import sys
import termios
import tty
import select
import time

tank_drive = MoveTank(OUTPUT_D, OUTPUT_A)

def get_key(timeout=0.01):
    dr, _, _ = select.select([sys.stdin], [], [], timeout)
    if dr:
        return sys.stdin.read(1)
    return None

def main():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    active_key = None
    last_key_time = 0
    hold_duration = 0.15  # how long to keep moving after last keypress

    try:
        while True:
            key = get_key()

            if key:
                if key == 'q':
                    break
                elif key in ['w', 'a', 's', 'd']:
                    active_key = key
                    last_key_time = time.time()

            # Stop movement if no key press in the last 150 ms
            if time.time() - last_key_time > hold_duration:
                active_key = None

            if active_key == 'w':
                tank_drive.on(50, 50)
            elif active_key == 's':
                tank_drive.on(-50, -50)
            elif active_key == 'a':
                tank_drive.on(-30, 30)
            elif active_key == 'd':
                tank_drive.on(30, -30)
            else:
                tank_drive.off()

            time.sleep(0.005)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        tank_drive.off()

if __name__ == "__main__":
    main()

