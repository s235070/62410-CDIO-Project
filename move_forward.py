#!/usr/bin/env python3
from ev3dev2.motor import MoveTank, OUTPUT_D, OUTPUT_A
from time import sleep

# Initialize a "tank" drive with large motors on outputs D and A
tank_drive = MoveTank(OUTPUT_D, OUTPUT_A)

# Move forward at speed=50 for 2 seconds
tank_drive.on_for_seconds(left_speed=50, right_speed=50, seconds=2)

# Stop motors
tank_drive.off()

