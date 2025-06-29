import cv2
import cv2.aruco as aruco
import numpy as np

# === Indlæs kalibreringsdata ===
data = np.load("calibration_data/camera_calibration.npz")
camera_matrix = data["camera_matrix"]
dist_coeffs = data["dist_coeffs"]

# === ArUco konfiguration ===
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
PARAMETERS = aruco.DetectorParameters()
MARKER_LENGTH = 0.05  # længde i meter

EV3_ID = 0  # ID på EV3'ens ArUco-tag

def detect_ev3(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = aruco.detectMarkers(gray, ARUCO_DICT, parameters=PARAMETERS)

    if ids is not None and len(corners) > 0:
        rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, MARKER_LENGTH, camera_matrix, dist_coeffs)

        for i, tag_id in enumerate(ids.flatten()):
            if tag_id == EV3_ID:
                rvec = rvecs[i][0]
                tvec = tvecs[i][0]
                center = np.mean(corners[i][0], axis=0)

                rotation_matrix, _ = cv2.Rodrigues(rvec)
                forward = rotation_matrix[:, 0]
                backward = -forward
                left = rotation_matrix[:, 1]
                right = -left

                def to_pixel(vec):
                    return (int(center[0] + 30 * vec[0]), int(center[1] + 30 * vec[1]))

                front = to_pixel(forward)
                back = to_pixel(backward)
                leftpt = to_pixel(left)
                rightpt = to_pixel(right)
                center_pt = (int(center[0]), int(center[1]))

                return front, back, leftpt, rightpt, center_pt

    return None, None, None, None, None
