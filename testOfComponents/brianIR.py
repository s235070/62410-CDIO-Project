#!/usr/bin/env python3

from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import InfraredSensor
from time import sleep

# Initialize tank drive on ports B & C
tank = MoveTank(OUTPUT_B, OUTPUT_C)

# Initialize Infrared Sensor on port S1 → 'in1'
ir = InfraredSensor('in1')
ir.mode = 'IR-PROX'  # measure proximity (0-100 scale)

try:
    while True:
        proximity = ir.proximity

        # If proximity is less than 15, assume an obstacle is close
        if proximity < 15:
            # Stop
            tank.off()

            # Turn left for 1 second
            tank.on_for_seconds(left_speed=-30, right_speed=30, seconds=1)
        else:
            # Drive forward at moderate speed
            tank.on(left_speed=30, right_speed=30)

        # Loop continuously, short pause for sensor reading
        sleep(0.1)

except KeyboardInterrupt:
    print("Stopping robot.")
    tank.off()
