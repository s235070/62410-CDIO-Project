import sys

import cv2
import numpy as np
import glob
import os

# Checkerboard-konfiguration (11x8 felter → 10x7 indvendige hjørner)
CHECKERBOARD = (10, 7)
SQUARE_SIZE = 0.015  # 15 mm i meter

objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

objpoints = []  # 3D virkelige punkter
imgpoints = []  # 2D billedepunkter

images = glob.glob("calibration_images/*.jpg")
print(f"[INFO] Antal billeder fundet: {len(images)}")

if not images:
    print("[FEJL] Ingen billeder fundet i calibration_images/")
    exit()

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)
        cv2.drawChessboardCorners(img, CHECKERBOARD, corners, ret)
        cv2.imshow("Checkerboard", img)
        cv2.waitKey(100)

cv2.destroyAllWindows()

# Kalibrér kameraet
ret, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

print("\n[KAMERA MATRIX]")
print(camera_matrix)
print("\n[DISTORTION]")
print(dist_coeffs)

# Gem resultatet
os.makedirs("calibration_data", exist_ok=True)
np.savez("calibration_data/camera_calibration.npz",
         camera_matrix=camera_matrix,
         dist_coeffs=dist_coeffs)

print("\n✅ Kalibrering gemt i: calibration_data/camera_calibration.npz")
# Gem kameramatricen og forvrængningskoefficienter til fil
np.savez("calibration_data/camera_calibration.npz", 
         camera_matrix=camera_matrix, 
         dist_coeffs=dist_coeffs)

print("[INFO] Kalibreringsdata gemt i calibration_data/camera_calibration.npz")
