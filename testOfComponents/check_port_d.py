#!/usr/bin/env python3
from ev3dev2.motor import Motor, OUTPUT_D
from ev3dev2 import DeviceNotFound

def check_port_d():
    try:
        motor = Motor(OUTPUT_D)
        motor_type = motor.driver_name

        if motor_type == 'lego-ev3-l-motor':
            print("Large motor is connected to port D.")
        elif motor_type == 'lego-ev3-m-motor':
            print("Medium motor is connected to port D.")
        else:
            print("Unknown motor type is connected to port D.")
    except DeviceNotFound:
        print("No motor is connected to port D.")

if __name__ == "__main__":
    check_port_d()

