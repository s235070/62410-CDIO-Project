#!/usr/bin/env python3

from ev3dev2.sensor.lego import UltrasonicSensor
import time

# Ultrasonic sensor is on port S3 → pass 'in3'
us = UltrasonicSensor('in3')

# Optional: ensure mode is distance in centimeters
us.mode = 'US-DIST-CM'

print("Ultrasonic Sensor Test. Press CTRL+C to exit.")

try:
    while True:
        distance_cm = us.distance_centimeters
        print("Distance: {:.2f} cm".format(distance_cm))
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting test.")

