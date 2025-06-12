from ultralytics import YOLO
from pathlib import Path
import torch
import cv2

# 🎯 Load YOLOv8 model
MODEL_PATH = Path(__file__).parent.parent / "models" / "best.pt"
model = YOLO(str(MODEL_PATH))

# 💻 Bestem device: GPU hvis muligt, ellers CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] YOLO model using device: {device}")

# 🟡 Boldtyper og farver
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
    try:
        results = model.predict(
            frame,
            conf=0.4,
            iou=0.3,
            verbose=False,
            device=device
        )
    except Exception as e:
        print(f"[WARN] GPU detection failed: {e}")
        print("[INFO] Switching to CPU")
        results = model.predict(
            frame,
            conf=0.4,
            iou=0.3,
            verbose=False,
            device='cpu'
        )

    detections = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            detections.append((label, (cx, cy)))

    return detections
