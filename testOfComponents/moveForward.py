#!/usr/bin/env python3
from ev3dev2.motor import MoveTank, OUTPUT_D, OUTPUT_A
from time import sleep

# Initialize tank drive
tank_drive = MoveTank(OUTPUT_D, OUTPUT_A)

# Move forward for 10 seconds
tank_drive.on_for_seconds(left_speed=50, right_speed=50, seconds=10)

# Move backward for 10 seconds
tank_drive.on_for_seconds(left_speed=-50, right_speed=-50, seconds=10)

# Turn left for 2 seconds (left motor backwards, right motor forward)
tank_drive.on_for_seconds(left_speed=-30, right_speed=30, seconds=2)

# Turn right for 4 seconds (left motor forward, right motor backwards)
tank_drive.on_for_seconds(left_speed=30, right_speed=-30, seconds=4)

# Move in a circle for 10 seconds (one motor faster than the other)
tank_drive.on_for_seconds(left_speed=20, right_speed=50, seconds=10)

# Stop motors
tank_drive.off()

