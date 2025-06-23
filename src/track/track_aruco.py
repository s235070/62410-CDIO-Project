import cv2
import numpy as np

CAMERA_INDEX = 0  # Skift til 1 hvis USB

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

camera_matrix = np.array([[800, 0, 320],
                          [0, 800, 240],
                          [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.zeros((5, 1))
marker_length = 0.05

cap = cv2.VideoCapture(CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("[ERROR] Could not open camera.")
    exit()

# Warm up camera
for _ in range(20):
    cap.read()

print("[INFO] Tracking started")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            corners, marker_length, camera_matrix, dist_coeffs)

        for i in range(len(ids)):
            tag_id = int(ids[i][0])
            tvec = tvecs[i][0]
            rvec = rvecs[i][0]

            # Udskriv position og rotation
            x, y, z = tvec
            rot_deg = np.rad2deg(np.linalg.norm(rvec))
            print(f"[ID {tag_id}] Pos: x={x:.2f}, y={y:.2f}, z={z:.2f} | Rot: {rot_deg:.1f}°")

            # Vi tegner IKKE drawAxis – for at undgå crash

    cv2.imshow("ArUco Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
