#!/usr/bin/env python3

import time
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C

# Initialize the motors
tank = MoveTank(OUTPUT_B, OUTPUT_C)

# Durations (seconds)
FORWARD_TIME = 30
CIRCLE_TIME  = 10

try:
    # 1) Drive straight for 30s
    print("Driving straight for {} seconds...".format(FORWARD_TIME))
    start_time = time.time()
    while time.time() - start_time < FORWARD_TIME:
        # According to your code, "straight forward" is (-30, -30)
        tank.on(left_speed=-30, right_speed=-30)
        time.sleep(0.1)
    tank.off()

    # 2) Drive in a circle for 10s
    print("Driving in a circle for {} seconds...".format(CIRCLE_TIME))
    start_time = time.time()
    while time.time() - start_time < CIRCLE_TIME:
        # Circle drive is (-30, +30)
        tank.on(left_speed=-30, right_speed=30)
        time.sleep(0.1)
    tank.off()

    # 3) Drive straight indefinitely
    print("Now driving straight indefinitely. Press CTRL+C to stop.")
    while True:
        # Again, "straight" is (-30, -30)
        tank.on(left_speed=-30, right_speed=-30)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping robot now.")
    tank.off()
