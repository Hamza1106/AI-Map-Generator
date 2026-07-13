"""
train.py - ML Model Training

"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from noise import generate_terrain_features

# Tile Types 
TILE_LABELS = {
    0: "Water",
    1: "Beach",
    2: "Plains",
    3: "Forest",
    4: "Mountain",
    5: "Snow"
}


def assign_tile_label(height: float, moisture: float, slope: float) -> int:
    """
    Rules:
        Water    → height very low
        Beach    → height moderate, slope flat
        Plains   → medium height, low moisture
        Forest   → medium height, high moisture
        Mountain → height high, slope steep
        Snow     → height very high (peak)
    """
    if height < 0.25:
        return 0  # Water

    if height < 0.32 and slope < 0.3:
        return 1  # Beach

    if height < 0.65:
        if moisture > 0.55:
            return 3  # Forest
        else:
            return 2  # Plains

    if height >= 0.85:
        return 5  # Snow

    return 4  # Mountain


def generate_training_data(num_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Generates Synthetic training data .
    Generate Terrain features → Assigning label by rules 
    """
    print(f"  -> Generating terrain features for {num_samples} samples...")

 
    np.random.seed(seed)
    all_rows = []

    # Multiple worlds 
    world_seeds = [42, 123, 456, 789, 1024]

    for ws in world_seeds:
        features = generate_terrain_features(width=40, height=25, seed=ws)

        h_map  = features["heightmap"]
        m_map  = features["moisture"]
        s_map  = features["slope"]
        n_map  = features["neighbor_avg"]
        rows, cols = h_map.shape

        for y in range(rows):
            for x in range(cols):
                height       = h_map[y][x]
                moisture     = m_map[y][x]
                slope        = s_map[y][x]
                neighbor_avg = n_map[y][x]
                label        = assign_tile_label(height, moisture, slope)

                all_rows.append({
                    "height":       round(height, 4),
                    "moisture":     round(moisture, 4),
                    "slope":        round(slope, 4),
                    "neighbor_avg": round(neighbor_avg, 4),
                    "label":        label
                })

    df = pd.DataFrame(all_rows)

    print(f"  -> Total samples generated: {len(df)}")
    print(f"  -> Tile distribution:")
    for label_id, label_name in TILE_LABELS.items():
        count = len(df[df["label"] == label_id])
        pct   = round(count / len(df) * 100, 1)
        print(f"       {label_name:10s} : {count:4d} ({pct}%)")

    return df


def train_models(df: pd.DataFrame) -> dict:
    """
    Checking for different models and comparing their performance.
       """
    X = df[["height", "moisture", "slope", "neighbor_avg"]]
    y = df["label"]

   
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        "Random Forest":  RandomForestClassifier(n_estimators=100, random_state=42),
        "Decision Tree":  DecisionTreeClassifier(random_state=42),
        "KNN":            KNeighborsClassifier(n_neighbors=5)
    }

    results = {}

    print("\n  -> Training & comparing models...\n")
    print(f"  {'Model':<20} {'Accuracy':>10} {'CV Score':>10}")
    print(f"  {'-'*42}")

    for name, model in models.items():
        
        model.fit(X_train, y_train)

       
        y_pred   = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

       
        cv_scores = cross_val_score(model, X, y, cv=5)
        cv_mean   = cv_scores.mean()

        print(f"  {name:<20} {accuracy*100:>9.2f}% {cv_mean*100:>9.2f}%")

        results[name] = {
            "model":    model,
            "accuracy": accuracy,
            "cv_score": cv_mean,
            "y_test":   y_test,
            "y_pred":   y_pred
        }

    return results


def save_best_model(results: dict, save_path: str = "models/tile_classifier.pkl"):
    
    
    best_name = max(results, key=lambda k: results[k]["accuracy"])
    best      = results[best_name]

    print(f"\n  -> Best model: {best_name} ({best['accuracy']*100:.2f}%)")

   
    print(f"\n  -> Classification Report ({best_name}):")
    report = classification_report(
        best["y_test"],
        best["y_pred"],
        target_names=list(TILE_LABELS.values())
    )
    for line in report.split("\n"):
        print(f"       {line}")

    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump({
        "model":      best["model"],
        "model_name": best_name,
        "accuracy":   best["accuracy"],
        "tile_labels": TILE_LABELS
    }, save_path)

    print(f"\n  -> Model saved to: {save_path}")
    return best["model"]



if __name__ == "__main__":
    print("=" * 50)
    print("   AI World Generator — Model Training")
    print("=" * 50)

    print("\n[1/3] Generating training data...")
    df = generate_training_data(seed=42)

    print("\n[2/3] Training models...")
    results = train_models(df)

    print("\n[3/3] Saving best model...")
    save_best_model(results, save_path="models/tile_classifier.pkl")

    print("\nTraining complete!")