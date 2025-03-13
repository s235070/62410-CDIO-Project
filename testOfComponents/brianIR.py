#!/usr/bin/env python3

import time
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import InfraredSensor

# Initialize motors on outputs B & C
tank = MoveTank(OUTPUT_B, OUTPUT_C)

# Initialize IR sensor on port S1: 'in1'
ir = InfraredSensor('in1')
ir.mode = 'IR-PROX'  # Returns a value 0..100 (0=very close, 100=far)

# Set a threshold for obstacle detection (adjust if needed)
OBSTACLE_THRESHOLD = 15

try:
    while True:
        # Read raw proximity value
        reading = ir.proximity

        # Print the reading for debugging
        print("IR Proximity reading:", reading)

        # Check if reading < threshold => obstacle
        if reading < OBSTACLE_THRESHOLD:
            # Stop motors and pause for 1 second
            tank.off()
            print("Obstacle detected, pausing for 1 second...")
            time.sleep(1)
        else:
            # Drive forward with negative speeds if that is forward for your robot
            tank.on(left_speed=-30, right_speed=-30)

        # Short delay to avoid spamming readings
        time.sleep(0.1)

except KeyboardInterrupt:
    print("CTRL+C pressed, stopping motors.")
    tank.off()
