#!/usr/bin/env python3

import time
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import InfraredSensor

# Initialize motors
tank = MoveTank(OUTPUT_B, OUTPUT_C)

# If you want IR for checking obstacles, uncomment the lines below:
# ir = InfraredSensor('in1')
# ir.mode = 'IR-PROX'

FORWARD_TIME = 30  # Drive forward for 30s
CIRCLE_TIME  = 10  # Drive in a circle for 10s

try:
    # 1) Drive straight for 30s
    #    Left motor = -30, Right motor = +30
    print("Driving straight for {} seconds...".format(FORWARD_TIME))
    start_time = time.time()
    while (time.time() - start_time) < FORWARD_TIME:
        tank.on(left_speed=-30, right_speed=30)
        time.sleep(0.1)
    tank.off()

    # 2) Drive in a circle for 10s
    #    Example circle: Left motor = -30, Right motor = -10
    print("Driving in a circle for {} seconds...".format(CIRCLE_TIME))
    start_time = time.time()
    while (time.time() - start_time) < CIRCLE_TIME:
        tank.on(left_speed=-30, right_speed=-10)
        time.sleep(0.1)
    tank.off()

    # 3) Drive straight indefinitely until Ctrl + C
    print("Now driving straight indefinitely. Press Ctrl+C to stop.")
    while True:
        tank.on(left_speed=-30, right_speed=30)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Caught Ctrl+C, stopping motors now.")
    tank.off()
