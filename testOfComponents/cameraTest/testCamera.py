import cv2
import numpy as np
import os

# EV3 SSH detaljer
EV3_IP = "172.20.10.8"  # SKAL ændres, hvis IP'en skifter
EV3_USER = "robot"

def send_ev3_command(command):
    """Sender en kommando til EV3 via SSH uden at bede om adgangskode"""
    full_command = f'ssh -o StrictHostKeyChecking=no {EV3_USER}@{EV3_IP} "python3 -c \'{command}\'"'
    print(f"Udfører SSH kommando: {full_command}")  # Debug print
    os.system(full_command)

# Åbn kamera interface 1 (ingen fallback til kamera 0)
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Fejl: Kamera 1 kunne ikke åbnes! Sørg for, at det er tilsluttet.")
    exit()

# Variabel til at tracke EV3's bevægelse
ev3_is_moving = False

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kan ikke modtage frame fra kamera 1. Afslutter...")
        break

    # Konverter billede til HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Definer farveområde for orange
    lower_orange = np.array([10, 100, 100])
    upper_orange = np.array([25, 255, 255])

    # Skab en maske
    mask = cv2.inRange(hsv, lower_orange, upper_orange)

    # Find konturer
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    ball_detected = False
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        if area > 100:
            ball_detected = True

    # Kun send SSH-kommando hvis tilstanden ændrer sig
    if ball_detected and not ev3_is_moving:
        print("Orange bold opdaget! Robot bevæger sig fremad.")
        send_ev3_command("from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C; tank=MoveTank(OUTPUT_B, OUTPUT_C); tank.on(30,30)")
        ev3_is_moving = True

    elif not ball_detected and ev3_is_moving:
        print("Ingen bold opdaget. Stopper.")
        send_ev3_command("from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C; tank=MoveTank(OUTPUT_B, OUTPUT_C); tank.off()")
        ev3_is_moving = False

    # Vis kamera-feed
    cv2.imshow('Kamera', frame)
    cv2.imshow('Maske', mask)

    # Forhindrer frysning
    cv2.waitKey(1)

    # Afslut ved at trykke 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Ryd op og luk ned
cap.release()
cv2.destroyAllWindows()
send_ev3_command("from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C; tank=MoveTank(OUTPUT_B, OUTPUT_C); tank.off()")
