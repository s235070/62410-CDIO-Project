#!/usr/bin/env python3
from ev3dev2.motor import MoveTank, MediumMotor, OUTPUT_D, OUTPUT_A, OUTPUT_C
import sys
import termios
import tty
import select
import time

# Initialize motors
tank_drive = MoveTank(OUTPUT_D, OUTPUT_A)
medium_motor = MediumMotor(OUTPUT_C)

def get_key(timeout=0.01):
    """Check for a key press with timeout"""
    dr, _, _ = select.select([sys.stdin], [], [], timeout)
    if dr:
        return sys.stdin.read(1)
    return None

def main():
    # Terminal setup
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    drive_key = None
    medium_key = None
    drive_last = 0
    medium_last = 0
    hold_time = 0.15  # key hold timeout in seconds

    try:
        while True:
            key = get_key()

            # Handle key press
            if key:
                if key == 'q':
                    break
                elif key in ['w', 'a', 's', 'd']:
                    drive_key = key
                    drive_last = time.time()
                elif key in ['f', 'b']:
                    medium_key = key
                    medium_last = time.time()

            # Reset keys if timeout passed
            if time.time() - drive_last > hold_time:
                drive_key = None
            if time.time() - medium_last > hold_time:
                medium_key = None

            # Handle tank drive
            if drive_key == 'w':
                tank_drive.on(50, 50)
            elif drive_key == 's':
                tank_drive.on(-50, -50)
            elif drive_key == 'a':
                tank_drive.on(-30, 30)
            elif drive_key == 'd':
                tank_drive.on(30, -30)
            else:
                tank_drive.off()

            # Handle medium motor
            if medium_key == 'f':
                medium_motor.on(50)
            elif medium_key == 'b':
                medium_motor.on(-50)
            else:
                medium_motor.off()

            time.sleep(0.005)

    finally:
        # Restore terminal and stop motors
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        tank_drive.off()
        medium_motor.off()

if __name__ == "__main__":
    main()

