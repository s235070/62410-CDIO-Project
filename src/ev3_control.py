# ev3_control.py

import paramiko
import time

# 🔧 IP-adressen til din EV3 (ændr hvis nødvendigt)
EV3_HOST = "172.20.10.2"
EV3_USER = "robot"
EV3_PASS = "maker"

# Intern status
_ssh_client = None
_last_cmd = None
_last_sent_time = 0
_COOLDOWN_SECONDS = 1.5  # Undgå spam

# 🔌 Opretter SSH-forbindelse til EV3
def setup_connection():
    global _ssh_client
    _ssh_client = paramiko.SSHClient()
    _ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        _ssh_client.connect(EV3_HOST, username=EV3_USER, password=EV3_PASS, timeout=5)
        print("[SSH] Forbindelse oprettet.")
    except Exception as e:
        print(f"[SSH ERROR] Kunne ikke forbinde til EV3: {e}")
        _ssh_client = None

# 🚀 Almindelig kommando (bruges ikke længere aktivt)
def send_command(cmd):
    global _ssh_client, _last_cmd, _last_sent_time
    if _ssh_client is None:
        print("[SSH ERROR] Ingen aktiv forbindelse (kald setup_connection først)")
        return

    now = time.time()
    if cmd == _last_cmd and (now - _last_sent_time) < _COOLDOWN_SECONDS:
        return  # Undgå gentagne samme kommandoer

    try:
        stdin, stdout, stderr = _ssh_client.exec_command(cmd)
        print("[SSH OUTPUT]", stdout.read().decode())
        _last_cmd = cmd
        _last_sent_time = now
    except Exception as e:
        print(f"[SSH ERROR] {e}")

# ✅ Sikker version (brug denne fra nu af!)
def send_safe_command(cmd):
    global _ssh_client, _last_cmd, _last_sent_time
    if _ssh_client is None:
        print("[SSH ERROR] Ingen aktiv forbindelse (kald setup_connection først)")
        return

    now = time.time()
    if cmd == _last_cmd and (now - _last_sent_time) < _COOLDOWN_SECONDS:
        print("[SSH] Kommando ignoreret pga. cooldown:", cmd)
        return

    try:
        stdin, stdout, stderr = _ssh_client.exec_command(cmd)
        print("[SSH OUTPUT]", stdout.read().decode())
        _last_cmd = cmd
        _last_sent_time = now
    except Exception as e:
        print(f"[SSH ERROR] {e}")

# ✅ Tilgængelige bevægelseskommandoer (match til move_robot.py)
CMD_FORWARD          = "python3 move_robot.py forward"
CMD_FORWARD_SLIGHT   = "python3 move_robot.py forward_slight"
CMD_FORWARD_LONG     = "python3 move_robot.py forward_long"
CMD_BACKWARD         = "python3 move_robot.py backward"
CMD_BACKWARD_SLIGHT  = "python3 move_robot.py backward_slight"
CMD_LEFT             = "python3 move_robot.py left"
CMD_LEFT_SLIGHT      = "python3 move_robot.py left_slight"
CMD_RIGHT            = "python3 move_robot.py right"
CMD_RIGHT_SLIGHT     = "python3 move_robot.py right_slight"
CMD_SPIN_LEFT        = "python3 move_robot.py spin_left"
CMD_SPIN_RIGHT       = "python3 move_robot.py spin_right"
CMD_STOP             = "python3 move_robot.py stop"
CMD_BACK_A_LITTLE = "python3 move_robot.py back_a_little"
