import subprocess
import time

class EV3Controller:
    def __init__(self, ip="192.168.0.30", user="robot"):
        print(f"[INFO] Connecting to {user}@{ip}...")
        self.ssh = subprocess.Popen(
            ["ssh", f"{user}@{ip}", "python3 /home/robot/ev3_listener.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        time.sleep(2)  # 🔧 Giv EV3 tid til at starte scriptet
        print("[✅] SSH connection established.")

    def send(self, command):
        try:
            self.ssh.stdin.write(command + "\n")
            self.ssh.stdin.flush()
            print(f"[SENT] {command}")
        except Exception as e:
            print(f"[ERROR] Could not send command: {command} ({e})")

    def stop(self):
        try:
            self.send("stop")
        except Exception:
            print("[INFO] Could not send stop command – SSH may be closed.")

    def close(self):
        try:
            self.send("stop")
            self.ssh.stdin.close()
            self.ssh.terminate()
            print("[INFO] SSH connection closed.")
        except Exception as e:
            print("[ERROR] Failed to close SSH:", e)
