#!/usr/bin/env python3

from ev3dev2.sensor.lego import ColorSensor
import time

# Initialize color sensor on port S3 → pass 'in3'
cs = ColorSensor('in3')
# Set sensor mode to color recognition
cs.mode = 'COL-COLOR'

print("Color Sensor Test. Press CTRL+C to exit.")

# Color codes (for reference):
# 0: No color
# 1: Black
# 2: Blue
# 3: Green
# 4: Yellow
# 5: Red
# 6: White
# 7: Brown

try:
    while True:
        color_id = cs.color
        print("Detected color ID:", color_id)
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting test.")

