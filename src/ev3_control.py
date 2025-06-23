# ev3_control.py
import paramiko
import time

EV3_HOST = "172.20.10.2"
EV3_USER = "robot"
EV3_PASS = "maker"

_ssh_client = None
_last_cmd = None
_last_sent_time = 0
_COOLDOWN_SECONDS = 1.5  # For at undgå spam og fejl

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

def send_command(cmd):
    global _ssh_client, _last_cmd, _last_sent_time
    if _ssh_client is None:
        print("[SSH ERROR] Ingen aktiv forbindelse (kald setup_connection først)")
        return

    now = time.time()
    if cmd == _last_cmd and (now - _last_sent_time) < _COOLDOWN_SECONDS:
        return  # skip samme kommando

    try:
        stdin, stdout, stderr = _ssh_client.exec_command(cmd)
        print("[SSH OUTPUT]", stdout.read().decode())
        _last_cmd = cmd
        _last_sent_time = now
    except Exception as e:
        print(f"[SSH ERROR] {e}")

# 🔁 Bruges i track.py
CMD_FORWARD = "python3 move_robot.py forward"
CMD_BACKWARD = "python3 move_robot.py backward"
CMD_LEFT = "python3 move_robot.py left"
CMD_RIGHT = "python3 move_robot.py right"
