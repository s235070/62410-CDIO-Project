import cv2
import os
from datetime import datetime
from config import CAMERA_INDEX

SAVE_DIR = "dataset/images"
os.makedirs(SAVE_DIR, exist_ok=True)

def main():
    print("[INFO] Starting camera...")

    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("[ERROR] Cannot access camera.")
        return

    print("[INFO] Press SPACE to save frame, ESC to quit.")
cv2.waitKey(2000)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Capture Dataset", frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(SAVE_DIR, f"{timestamp}.jpg")
            cv2.imwrite(filename, frame)
            print(f"[SAVED] {filename}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
frame_count = 0  # Tilføj udenfor while-loopet

# Inde i if key == 32-blokken:
frame_count += 1
print(f"[INFO] Total frames saved: {frame_count}")
