from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from time import sleep

# Test hvilke porte har tilsluttede motorer
for port in [OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D]:
    try:
        m = LargeMotor(port)
        m.on_for_seconds(20, 1)
        print(f"Motor works on {port}")
    except:
        print(f"No motor on {port}")

