from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank
from time import sleep

# Motor setup
tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)     # Kørsel (venstre og højre hjul)
claw_motor = MediumMotor(OUTPUT_A)            # Claw (gribearm)
pusher_motor = MediumMotor(OUTPUT_D)          # Pusher (skubber bold ind i mål)

# === BEVÆGELSE ===

def move_forward(duration=1.0, speed=40):
    tank_drive.on_for_seconds(SpeedPercent(speed), SpeedPercent(speed), duration)

def move_backward(duration=1.0, speed=40):
    tank_drive.on_for_seconds(SpeedPercent(-speed), SpeedPercent(-speed), duration)

def spin_left(duration=0.5, speed=40):
    tank_drive.on_for_seconds(SpeedPercent(-speed), SpeedPercent(speed), duration)

def spin_right(duration=0.5, speed=40):
    tank_drive.on_for_seconds(SpeedPercent(speed), SpeedPercent(-speed), duration)

def turn_left_a_little():
    spin_left(duration=0.2, speed=20)

def turn_right_a_little():
    spin_right(duration=0.2, speed=20)

def spin_around():
    spin_right(duration=1.0, speed=50)

def stop():
    tank_drive.off()

# === CLAW ===

def claw_open():
    claw_motor.on_for_degrees(SpeedPercent(30), -90)  # Åbner kloen

def claw_close():
    claw_motor.on_for_degrees(SpeedPercent(30), 90)   # Lukker kloen

# === PUSHER ===

def pusher_extend():
    pusher_motor.on_for_degrees(SpeedPercent(50), 180)  # Skub ud

def pusher_retract():
    pusher_motor.on_for_degrees(SpeedPercent(50), -180) # Træk ind

# === TEST-SEKVENS ===

if _name_ == '_main_':
    print("Test bevægelser og mekanismer...")
    move_forward()
    sleep(1)
    spin_right()
    sleep(1)
    move_backward()
    sleep(1)
    claw_open()
    sleep(0.5)
    claw_close()
    sleep(0.5)
    pusher_extend()
    sleep(0.5)
    pusher_retract()
    print("Done.")
move_robot.py