
#!/usr/bin/env python3

from ev3dev2.sensor.lego import TouchSensor
import time

# Touch sensor on port S1 → pass 'in1'
ts = TouchSensor('in1')

print("Touch Sensor Test. Press CTRL+C to exit.")

try:
    while True:
        if ts.is_pressed:
            print("Touch sensor is PRESSED!")
        else:
            print("Touch sensor is NOT pressed.")
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting test.")

