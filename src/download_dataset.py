from roboflow import Roboflow

# Brug din egen API-nøgle og workspace/projekt/version
rf = Roboflow(api_key="h6m7QEqT6Po9FCmTAPUH")
project = rf.workspace("balldetection-z7gmn").project("ball-detection-mobgq")
version = project.version(2)  # Brug v2
dataset = version.download("yolov8")