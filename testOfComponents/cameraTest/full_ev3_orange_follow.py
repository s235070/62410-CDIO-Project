#!/usr/bin/env python3

import time
import subprocess
from PIL import ImageGrab
import numpy as np

# The IP address (or hostname) of your EV3
EV3_IP = "172.20.10.8"  

# The path to move_robot.py on the EV3
REMOTE_SCRIPT = "/home/robot/62410-CDIO-Project/testOfComponents/cameraTest/move_robot.py"

# Camera index on your laptop (0 = built-in, 1 = USB, etc.)
CAMERA_INDEX = 1

# HSV range for detecting orange
# Adjust if your lighting/orange shade is different
LOWER_ORANGE = np.array([10, 100, 100])
UPPER_ORANGE = np.array([25, 255, 255])

# If the ball's area is above this, we consider it "close"
AREA_CLOSE_THRESHOLD = 2000

# Function to send command to EV3
def send_command(cmd):
    try:
        subprocess.run(["ssh", f"robot@{EV3_IP}", "python3", REMOTE_SCRIPT, cmd], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error sending command '{cmd}' to EV3: {e}")

# Main Script
def main():
    print("Starting camera loop.")
    
    while True:
        # Grab an image from the screen (replace this with your camera capture code)
        image = ImageGrab.grab(bbox=(0, 0, 640, 480))  # Change the coordinates to capture the camera feed
        image_np = np.array(image)
        
        # Convert to HSV for color detection
        hsv = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV)
        
        # Create a binary mask for "orange"
        mask = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            
            if area > AREA_CLOSE_THRESHOLD:
                send_command("stop")  # Stop the robot if the ball is close
            else:
                send_command("forward")  # Otherwise, move forward
        else:
            send_command("stop")  # Stop if no ball is detected
        
        time.sleep(0.1)  # Adjust the delay as needed

if __name__ == "__main__":
    main()
