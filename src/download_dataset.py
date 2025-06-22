from roboflow import Roboflow
rf = Roboflow(api_key="h6m7QEqT6Po9FCmTAPUH")
project = rf.workspace("balldetection-z7gmn").project("ev3-ld4mh")
version = project.version(1)
dataset = version.download("yolov8")
