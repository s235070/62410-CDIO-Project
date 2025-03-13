#!/usr/bin/env python3
import glob

base_path = "/sys/class/lego-sensor"
sensors = glob.glob(base_path + "/sensor*")

if not sensors:
    print("No sensors detected.")
else:
    for sensor in sensors:
        try:
            with open(sensor + "/address", 'r') as f:
                port_address = f.read().strip()
            with open(sensor + "/driver_name", 'r') as f:
                driver_name = f.read().strip()

            print("Sensor directory: {}".format(sensor))
            print("Port address: {}".format(port_address))
            print("Driver: {}".format(driver_name))
            print("-----")
        except OSError as e:
            print("Error reading sensor info from {}: {}".format(sensor, e))


