from ultralytics import YOLO
import shutil
import os

def main():
    # === PATHS ===
    data_yaml_path = "src/yolov8/track-system-6/data.yaml"
    model_output_dir = "runs/train/track-systemV1.6/weights"
    final_model_dest = "src/models/best.pt"

    # === TRÆNING ===
    model = YOLO("yolov8s.pt")
    model.train(
        data=data_yaml_path,
        epochs=150,
        imgsz=640,
        batch=16,
        project="runs/train",
        name="track-systemV1.6",
        exist_ok=True,
        optimizer="Adam",
        lr0=0.001,
        lrf=0.01,
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
        degrees=10.0, translate=0.1, scale=0.5, shear=2.0,
        perspective=0.0005, fliplr=0.5,
        mosaic=1.0, mixup=0.2,
        patience=30
    )

    # === KOPIÉR best.pt TIL MODELS-MAPPE ===
    best_model_path = os.path.join(model_output_dir, "best.pt")
    if os.path.exists(best_model_path):
        shutil.copy(best_model_path, final_model_dest)
        print(f"[✓] Trænet model gemt som: {final_model_dest}")
    else:
        print("[!] Kunne ikke finde best.pt – check at træning lykkedes.")

# 👇 VIGTIGT på Windows:
if __name__ == "__main__":
    main()