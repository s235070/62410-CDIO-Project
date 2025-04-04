#!/usr/bin/env python3
from ev3dev2.sensor.lego import InfraredSensor
from time import sleep

# Initialiser IR-sensoren paa port in1
ir = InfraredSensor(address='ev3-ports:in1')

# Laes og print afstand kontinuerligt
print("Starter IR-sensor laesning...")
while True:
    distance = ir.proximity  # Laes naerheds-vaerdi
    print("Afstand: {}".format(distance))
    sleep(0.5)

