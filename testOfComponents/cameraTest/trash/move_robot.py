#!/usr/bin/env python3
import sys
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C

tank = MoveTank(OUTPUT_B, OUTPUT_C)

if len(sys.argv) < 2:
    print("Usage: move_robot.py [forward|left|right|stop]")
    sys.exit()

cmd = sys.argv[1]

if cmd == "forward":
    tank.on(left_speed=-30, right_speed=-30)  # Adjust if your robot orientation is reversed
elif cmd == "left":
    tank.on(left_speed=30, right_speed=-30)
elif cmd == "right":
    tank.on(left_speed=-30, right_speed=30)
elif cmd == "stop":
    tank.off()
else:
    print("Unknown command:", cmd)
