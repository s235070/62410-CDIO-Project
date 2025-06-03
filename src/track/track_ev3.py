import cv2
import numpy as np
import math

green_lower = np.array([40, 40, 40])
green_upper = np.array([90, 255, 255])
kernel = np.ones((5, 5), np.uint8)

def circularity(cnt):
    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)
    if perimeter == 0:
        return 0
    return 4 * np.pi * area / (perimeter ** 2)

def detect_ev3(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, green_lower, green_upper)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 100 or area > 5000:
            continue
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        circ = circularity(cnt)
        valid.append({'cnt': cnt, 'center': (cx, cy), 'circ': circ})

    best_pair = None
    best_distance = float('inf')

    for i in range(len(valid)):
        for j in range(i + 1, len(valid)):
            pt1 = valid[i]['center']
            pt2 = valid[j]['center']
            dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
            if dist < 100 and dist < best_distance:
                best_distance = dist
                best_pair = (valid[i], valid[j])

    if best_pair:
        a, b = best_pair
        front, back = (a['center'], b['center']) if a['circ'] > b['circ'] else (b['center'], a['center'])
        return front, back
    else:
        return None, None
