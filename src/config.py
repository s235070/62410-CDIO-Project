from pathlib import Path

# ====== CAMERA SETTINGS ======
DISABLE_MSMF = True
CAMERA_INDEX = 0  

# ====== PROJECT STRUCTURE ======
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Gets the root folder
PROFILE_DIR = PROJECT_ROOT / "camera_profiles"
ASSETS_DIR = PROJECT_ROOT / "assets"

# ====== CAMERA SETTINGS ======
WARP_WIDTH = 640   # Output resolution of warped image
WARP_HEIGHT = 480

# ====== EV3 SETTINGS ======
EV3_IP = "172.20.10.6" # Baseret på vores mobildata. 
EV3_USER = "robot"
