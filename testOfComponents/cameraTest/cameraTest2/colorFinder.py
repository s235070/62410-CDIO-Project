import cv2
import numpy as np

def show_hsv_from_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = hsv[y, x]
        print(f"Clicked HSV at ({x}, {y}): {pixel}")

img = cv2.imread("image.png")  # ← skift til din sti hvis det er en anden
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

cv2.namedWindow("Click to get HSV")
cv2.setMouseCallback("Click to get HSV", show_hsv_from_click)

while True:
    cv2.imshow("Click to get HSV", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
