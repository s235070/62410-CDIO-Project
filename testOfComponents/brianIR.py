#!/usr/bin/env python3

import time
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import InfraredSensor

# Initialize motors and IR sensor
tank = MoveTank(OUTPUT_B, OUTPUT_C)
ir = InfraredSensor('in1')  # e.g., IR sensor on port S1
ir.mode = 'IR-PROX'         # returns values 0-100

# Define some settings
OBSTACLE_THRESHOLD = 25  # stop if IR < 25
FORWARD_SPEED = (-30, 30) # negative speed if your robot is reversed
CIRCLE_SPEED  = (-30, -10) # or any speed combo for circular motion

# Time durations
FORWARD_TIME  = 30  # drive forward for 30s
CIRCLE_TIME   = 10  # then circle for 10s

def drive_with_obstacle_check(left_speed, right_speed, duration):
    """
    Drives for 'duration' seconds at the given speeds.
    If IR < OBSTACLE_THRESHOLD, stop for 1s and then continue.
    """
    start_t = time.time()
    while time.time() - start_t < duration:
        proximity = ir.proximity
        if proximity < OBSTACLE_THRESHOLD:
            # Stop if obstacle is close
            tank.off()
            print("Obstacle detected (<{}). Pausing 1s...".format(OBSTACLE_THRESHOLD))
            time.sleep(1)
        else:
            # Drive
            tank.on(left_speed=left_speed, right_speed=right_speed)
        
        time.sleep(0.1)
    # Stop at the end of this phase
    tank.off()

try:
    # 1) Drive forward for 30s
    print("Driving forward for {} seconds...".format(FORWARD_TIME))
    drive_with_obstacle_check(FORWARD_SPEED[0], FORWARD_SPEED[1], FORWARD_TIME)

    # 2) Drive in a circle for 10s
    print("Driving in a circle for {} seconds...".format(CIRCLE_TIME))
    drive_with_obstacle_check(CIRCLE_SPEED[0], CIRCLE_SPEED[1], CIRCLE_TIME)

    # 3) Resume forward driving indefinitely
    print("Now driving forward indefinitely (Ctrl + C to stop).")
    while True:
        proximity = ir.proximity
        if proximity < OBSTACLE_THRESHOLD:
            # Stop if obstacle is close
            tank.off()
            print("Obstacle detected (<{}). Pausing 1s...".format(OBSTACLE_THRESHOLD))
            time.sleep(1)
        else:
            tank.on(left_speed=FORWARD_SPEED[0], right_speed=FORWARD_SPEED[1])
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nCTRL+C detected, stopping the robot.")
    tank.off()
