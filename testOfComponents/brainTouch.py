#!/usr/bin/env python3

import time
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import TouchSensor

# Motors on outputs B & C
tank = MoveTank(OUTPUT_B, OUTPUT_C)

# Touch Sensor on port S1 → 'in1'
ts = TouchSensor('in1')

try:
    while True:
        # If touch sensor is pressed
        if ts.is_pressed:
            tank.off()
            print("Touch sensor pressed! Turning 180 degrees...")

            # Perform a 180° turn
            # Adjust 'seconds' or 'speeds' below so the robot truly rotates ~180
            tank.on_for_seconds(left_speed=30, right_speed=-30, seconds=2)

            # After the turn, continue forward
            print("Turn complete. Driving forward again.")
            tank.on(left_speed=-30, right_speed=-30)

        else:
            # Drive forward if not pressed
            tank.on(left_speed=-30, right_speed=-30)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("CTRL+C detected, stopping.")
    tank.off()
