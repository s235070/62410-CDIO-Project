import numpy as np
import json
from pathlib import Path
from config import PROFILE_DIR

def load_matrix(label):
    """
    Loads the perspective matrix from profile directory.
    Returns:
        matrix (np.ndarray) or None
    """
    matrix_path = PROFILE_DIR / f"{label}_matrix.npy"
    if not matrix_path.exists():
        print("[ERROR] Matrix not found at:", matrix_path)
        return None
    return np.load(matrix_path)

def load_wall_profiles():
    """
    Loads HSV profiles for wall detection.
    Returns:
        dictionary of named profiles
    """
    profile_path = PROFILE_DIR / "wall_profiles.json"
    if not profile_path.exists():
        print("[ERROR] Wall profile JSON not found at:", profile_path)
        return None
    with open(profile_path, "r") as f:
        return json.load(f)

def ask_for_label():
    """
    Prompts user to enter a lighting label.
    """
    return input("Enter saved scenario label (e.g. dim): ").strip().lower()
