#!/usr/bin/env python3

from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import UltrasonicSensor
from time import sleep

# Initialize tank drive on ports B & C
tank = MoveTank(OUTPUT_B, OUTPUT_C)

# Initialize ultrasonic sensor on port S1 (use 'in1')
us = UltrasonicSensor('in1')
us.mode = 'US-DIST-CM'  # measure distance in cm

try:
    while True:
        distance = us.distance_centimeters

        # If an obstacle is within 4 cm, turn away
        if distance < 10:
            # Stop before turning
            tank.off()

            # Turn left for 1 second (adjust speeds/time as desired)
            tank.on_for_seconds(left_speed=-30, right_speed=30, seconds=2)
        else:
            # Drive forward indefinitely
            tank.on(left_speed=-30, right_speed=-30)

        # Check again after a short delay
        sleep(0.1)

except KeyboardInterrupt:
    print("Stopping robot.")
    tank.off()
