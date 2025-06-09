import numpy as np
from pathlib import Path
from config import PROFILE_DIR

def ask_for_label():
    """Prompt user for lighting scenario label"""
    return input("Enter lighting scenario label (e.g. bright, dim): ").strip().lower()

def load_matrix(label):
    """Load homography matrix for given label"""
    file_path = PROFILE_DIR / f"{label}_matrix.npy"
    try:
        return np.load(file_path)
    except FileNotFoundError:
        print(f"Matrix not found: {file_path}")
        print("Please run setup_camera_stand.py first")
        return None