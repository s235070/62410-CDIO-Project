from roboflow import Roboflow
rf = Roboflow(api_key="h6m7QEqT6Po9FCmTAPUH")
project = rf.workspace("balldetection-z7gmn").project("ball-detection-mobgq")
version = project.version(6)
dataset = version.download("yolov8")