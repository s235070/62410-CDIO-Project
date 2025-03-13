#!/usr/bin/env python3

from ev3dev2.sensor.lego import GyroSensor
import time

# Assume Gyro is on port S1 → 'in1'
gyro = GyroSensor('in1')
gyro.mode = 'GYRO-ANG'  # 'GYRO-ANG' for angle, 'GYRO-RATE' for deg/sec

print("Gyro Sensor Test (Angle mode). Press Ctrl+C to stop.")

try:
    while True:
        angle = gyro.angle
        print("Current angle:", angle)
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting Gyro test.")