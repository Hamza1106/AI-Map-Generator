"""
classifier.py - Tile Prediction using Trained ML Model

"""

import numpy as np
import pandas as pd
import joblib
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from noise import generate_terrain_features


TILE_LABELS = {
    0: "Water",
    1: "Beach",
    2: "Plains",
    3: "Forest",
    4: "Mountain",
    5: "Snow"
}

TILE_SYMBOLS = {
    0: "≈",   # Water
    1: ".",   # Beach
    2: "_",   # Plains
    3: "T",   # Forest
    4: "#",   # Mountain
    5: "^"    # Snow
}

TILE_COLORS = {
    0: "\033[94m",   # Blue   - Water
    1: "\033[93m",   # Yellow - Beach
    2: "\033[92m",   # Green  - Plains
    3: "\033[32m",   # Dark Green - Forest
    4: "\033[90m",   # Gray   - Mountain
    5: "\033[97m"    # White  - Snow
}

RESET = "\033[0m"


def load_model(model_path: str = "models/tile_classifier.pkl"):
    
    if not os.path.exists(model_path):
        print(f"  Model not found: {model_path}")
        print(f"  → Run First 'python src/train.py' ")
        sys.exit(1)

    data = joblib.load(model_path)
    print(f"  -> Model loaded: {data['model_name']} (accuracy: {data['accuracy']*100:.2f}%)")
    return data["model"]


def classify_world(features: dict, model) -> np.ndarray:
    """
    Input  : terrain features dict (noise.py se)
    Output : 2D numpy array of tile labels (0-5)
    """
    h_map  = features["heightmap"]
    m_map  = features["moisture"]
    s_map  = features["slope"]
    n_map  = features["neighbor_avg"]

    height, width = h_map.shape
    tile_map = np.zeros((height, width), dtype=int)

    
    for y in range(height):
        for x in range(width):
            # 4 features ek row mein
            tile_features = pd.DataFrame([[
                h_map[y][x],
                m_map[y][x],
                s_map[y][x],
                n_map[y][x]
            ]], columns=["height", "moisture", "slope", "neighbor_avg"])
            tile_map[y][x] = model.predict(tile_features)[0]

    return tile_map




if __name__ == "__main__":
    print("=" * 50)
    print("   AI World Generator — Classifier Test")
    print("=" * 50)

    print("\n[1/3] Loading model...")
    model = load_model("models/tile_classifier.pkl")

    print("\n[2/3] Generating terrain...")
    features = generate_terrain_features(width=40, height=20, seed=42)

    print("\n[3/3] Classifying world...")
    tile_map       = classify_world(features, model)

    print("\nclassifier.py working correctly!")