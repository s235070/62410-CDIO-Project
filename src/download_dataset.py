from roboflow import Roboflow
rf = Roboflow(api_key="xxxxxxxxxxxxxxxxxxxxxxxxx")
project = rf.workspace("xxxxxxxxxxxxxxxxxxxxxx").project("xxxxxxxxxxxxxxxxxxxxxxx")
version = project.version(6)
dataset = version.download("yolov8")
