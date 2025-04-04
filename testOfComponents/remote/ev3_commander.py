import subprocess

class EV3Controller:
    def __init__(self, ip="192.168.0.30", user="robot"):
        self.ip = ip
        self.user = user
        try:
            print(f"[INFO] Connecting to {user}@{ip}...")
            self.ssh = subprocess.Popen(
                ["ssh", f"{user}@{ip}", "python3 /home/robot/ev3_listener.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            print("[✅] SSH connection established.")
        except Exception as e:
            print(f"[❌] SSH connection failed: {e}")

    def send(self, command):
        try:
            self.ssh.stdin.write(command + "\n")
            self.ssh.stdin.flush()
            print("[SENT]", command)
        except Exception as e:
            print(f"[ERROR] Could not send command: {command} ({e})")

    def stop(self):
        try:
            self.send("stop")
        except:
            print("[INFO] Could not send stop command – SSH may be closed.")

