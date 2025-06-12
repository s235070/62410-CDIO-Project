from ev3_control import send_command, CMD_FORWARD

print("[TEST] Forsøger at sende kommando...")

try:
    send_command(CMD_FORWARD)
    print("[TEST] Kommando sendt (FORWARD)")
except Exception as e:
    print(f"[TEST FEJL] {e}")
