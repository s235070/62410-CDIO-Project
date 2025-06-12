from ultralytics import YOLO
from pathlib import Path
import cv2

# Indlæs den trænet model én gang
MODEL_PATH = Path(__file__).parent.parent / "models" / "best.pt"
model = YOLO(str(MODEL_PATH))

# Farver til boldtyper
COLOR_BGR = {
    "white_ball": (255, 255, 255),
    "orange_ball": (0, 165, 255),
    "ball": (0, 255, 255)  # fallback
}

def detect_balls_yolo(frame):
    """
    Detekterer bolde i billedet vha. YOLOv8-model.
    Returnerer liste over (label, (x, y))-positioner.
    """
    results = model.predict(frame, conf=0.4, iou=0.3, verbose=False)
    detections = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            detections.append((label, (cx, cy)))

    return detections
