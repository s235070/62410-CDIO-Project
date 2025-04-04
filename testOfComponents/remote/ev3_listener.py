#!/usr/bin/env python3
from ev3dev2.motor import MoveTank, OUTPUT_D, OUTPUT_A
import sys
import math
import time

# Initialiser motorer
tank = MoveTank(OUTPUT_D, OUTPUT_A)
print("EV3 is ready and listening for commands via SSH...")

def run_command(command):
    if command.startswith("turn"):
        _, angle_str = command.split()
        angle = int(angle_str)
        duration = abs(angle) * 0.01  # justér for din robot

        if angle > 0:
            tank.on(-30, 30)
        else:
            tank.on(30, -30)

        time.sleep(duration)
        tank.off()

    elif command.startswith("forward"):
        _, dist_str = command.split()
        dist = int(dist_str)
        duration = dist * 0.015  # justér for din robot

        tank.on(40, 40)
        time.sleep(duration)
        tank.off()

    elif command == "stop":
        tank.off()

    else:
        print("Unknown command:", command)

# Hovedløkke
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    print("Received command:", repr(line))
    try:
        run_command(line)
    except Exception as e:
        print("Error running command:", e)

