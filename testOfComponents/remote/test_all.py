#!/usr/bin/env python3
import sys
import termios
import tty
import select
import time

from ev3dev2.motor import (
    MoveTank,
    MediumMotor,
    OUTPUT_A,
    OUTPUT_B,
    OUTPUT_C,
    OUTPUT_D
)
from ev3dev2.sensor.lego import (
    GyroSensor,
    UltrasonicSensor,
    ColorSensor,
    InfraredSensor
)
from ev3dev2.sensor import (
    INPUT_1,
    INPUT_2,
    INPUT_3,
    INPUT_4
)

###############################################################################
# Configuration
###############################################################################
# Tank drive (large motors) on outD (left) and outA (right):
tank_drive = MoveTank(OUTPUT_D, OUTPUT_A)

# Medium motors on outC and outB:
medium_motor_c = MediumMotor(OUTPUT_C)
medium_motor_b = MediumMotor(OUTPUT_B)

# Sensors (adjust if needed):
gyro = GyroSensor(INPUT_1)
gyro.mode = 'GYRO-ANG'

us = UltrasonicSensor(INPUT_2)
us.mode = 'US-DIST-CM'

color = ColorSensor(INPUT_3)
color.mode = 'COL-REFLECT'

ir = InfraredSensor(INPUT_4)
ir.mode = 'IR-PROX'  # Reads proximity [0..100]

###############################################################################
# Helper function for non-blocking keyboard input
###############################################################################
def get_key(timeout=0.01):
    """
    Check for a single key press within 'timeout' seconds.
    Returns the character if pressed, or None if no key.
    """
    dr, _, _ = select.select([sys.stdin], [], [], timeout)
    if dr:
        return sys.stdin.read(1)
    return None

###############################################################################
# Main
###############################################################################
def main():
    # Prepare terminal to receive single-keystroke input
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    # Variables to hold which key we last pressed
    drive_key = None
    medium_key_c = None
    medium_key_b = None
    sensor_key = None  # for reading sensors

    # Timestamps for controlling how long we keep an action
    drive_last = 0
    medium_last_c = 0
    medium_last_b = 0
    sensor_last = 0

    hold_time = 0.15  # seconds to keep an action going after the last key press

    print("""
Use the following keys to control the robot:
  W  = drive forward
  S  = drive backward
  A  = turn left
  D  = turn right
  F  = Medium motor C forward
  B  = Medium motor C backward
  G  = Medium motor B forward
  H  = Medium motor B backward

Press R to read sensor values once.
Press Q to quit.
""")

    try:
        while True:
            key = get_key()

            # Check for a new key press
            if key:
                if key.lower() == 'q':
                    # Quit
                    break
                elif key in ['w', 'a', 's', 'd']:
                    drive_key = key
                    drive_last = time.time()
                elif key in ['f', 'b']:
                    medium_key_c = key
                    medium_last_c = time.time()
                elif key in ['g', 'h']:
                    medium_key_b = key
                    medium_last_b = time.time()
                elif key in ['r', 'R']:
                    sensor_key = 'r'
                    sensor_last = time.time()

            # Cancel motor actions if time has passed
            if time.time() - drive_last > hold_time:
                drive_key = None
            if time.time() - medium_last_c > hold_time:
                medium_key_c = None
            if time.time() - medium_last_b > hold_time:
                medium_key_b = None
            if time.time() - sensor_last > hold_time:
                sensor_key = None

            # ---- Tank drive logic ----
            if drive_key == 'w':
                # Forward
                tank_drive.on(50, 50)
            elif drive_key == 's':
                # Backward
                tank_drive.on(-50, -50)
            elif drive_key == 'a':
                # Left turn
                tank_drive.on(-30, 30)
            elif drive_key == 'd':
                # Right turn
                tank_drive.on(30, -30)
            else:
                tank_drive.off()

            # ---- Medium motor on outC ----
            if medium_key_c == 'f':
                medium_motor_c.on(50)
            elif medium_key_c == 'b':
                medium_motor_c.on(-50)
            else:
                medium_motor_c.off()

            # ---- Medium motor on outB ----
            if medium_key_b == 'g':
                medium_motor_b.on(50)
            elif medium_key_b == 'h':
                medium_motor_b.on(-50)
            else:
                medium_motor_b.off()

            # ---- Read sensor values if "R" was pressed ----
            if sensor_key == 'r':
                # Retrieve sensor values
                gyro_val = gyro.angle
                dist_cm = us.distance_centimeters
                color_val = color.reflected_light_intensity
                ir_val = ir.proximity

                # Print them
                print("Sensor readings:")
                print("  Gyro Angle      = {}".format(gyro_val))
                print("  Ultrasonic (cm) = {:.1f}".format(dist_cm))
                print("  Color Reflect   = {}".format(color_val))
                print("  IR Proximity    = {}".format(ir_val))
                print("")

            time.sleep(0.005)

    finally:
        # Restore terminal settings and stop motors
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        tank_drive.off()
        medium_motor_c.off()
        medium_motor_b.off()
        print("Exiting. All motors stopped.")

if __name__ == "__main__":
    main()
