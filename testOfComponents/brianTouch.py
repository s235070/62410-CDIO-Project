#!/usr/bin/env python3

import time
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import TouchSensor

# Motors on outputs B & C
tank = MoveTank(OUTPUT_B, OUTPUT_C)

# Touch Sensor on S1 ("in1")
ts = TouchSensor('in1')

try:
    while True:
        # Check if touch sensor is pressed
        if ts.is_pressed:
            tank.off()
            print("Touch sensor is PRESSED. Pausing for 1s...")
            time.sleep(1)
        else:
            # Drive forward at negative speeds if your robot is reversed
            tank.on(left_speed=-30, right_speed=-30)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("CTRL+C detected, stopping.")
    tank.off()
time.sleep(0.1)  # wait a bit before exiting