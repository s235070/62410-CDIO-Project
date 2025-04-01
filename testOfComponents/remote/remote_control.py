#!/usr/bin/env python3
from ev3dev2.motor import MoveTank, OUTPUT_D, OUTPUT_A
from time import sleep

tank_drive = MoveTank(OUTPUT_D, OUTPUT_A)

def move(cmd):
    if cmd == "w":
        print("Forward")
        tank_drive.on_for_seconds(50, 50, 1)
    elif cmd == "s":
        print("Backward")
        tank_drive.on_for_seconds(-50, -50, 1)
    elif cmd == "a":
        print("Left")
        tank_drive.on_for_seconds(-30, 30, 1)
    elif cmd == "d":
        print("Right")
        tank_drive.on_for_seconds(30, -30, 1)
    elif cmd == "c":
        print("Circle")
        tank_drive.on_for_seconds(20, 50, 10)
    elif cmd == "q":
        print("Quitting.")
        return False
    else:
        print("Unknown command. Use: w/s/a/d/c/q")
    tank_drive.off()
    return True

def main():
    print("Manual Control:")
    print(" w = forward\n s = backward\n a = left\n d = right\n c = circle\n q = quit")
    running = True
    while running:
        cmd = input("Command: ").strip().lower()
        running = move(cmd)

if __name__ == "__main__":
    main()

