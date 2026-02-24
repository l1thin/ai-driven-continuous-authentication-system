import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# ---------------- PATH SETUP ---------------- #

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FEATURE_DIR = os.path.join(BASE_DIR, "data", "features")
MODEL_DIR = os.path.join(BASE_DIR, "models")
STATE_FILE = os.path.join(BASE_DIR, "system_state.json")

if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

# -------------------------------------------- #


def load_features(filename):
    path = os.path.join(FEATURE_DIR, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"{filename} not found in features directory.")

    df = pd.read_csv(path)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    if df.empty:
        raise ValueError(f"{filename} is empty after cleaning.")

    return df


def train_models():

    print("\n[INFO] Loading feature datasets...")

    key_df = load_features("keystroke_features.csv")
    mouse_df = load_features("mouse_features.csv")
    click_df = load_features("click_features.csv")

    print("[INFO] Feature sizes:")
    print("Keystroke:", len(key_df))
    print("Mouse:", len(mouse_df))
    print("Click:", len(click_df))

    # ---------------- SCALING ---------------- #

    key_scaler = StandardScaler()
    mouse_scaler = StandardScaler()
    click_scaler = StandardScaler()

    key_scaled = key_scaler.fit_transform(key_df)
    mouse_scaled = mouse_scaler.fit_transform(mouse_df)
    click_scaled = click_scaler.fit_transform(click_df)

    # ---------------- MODELS ---------------- #

    print("\n[INFO] Training models...")

    key_model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )
    key_model.fit(key_scaled)

    mouse_model = OneClassSVM(
        kernel="rbf",
        nu=0.05,
        gamma="scale"
    )
    mouse_model.fit(mouse_scaled)

    click_model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )
    click_model.fit(click_scaled)

    # ---------------- SAVE MODELS ---------------- #

    joblib.dump(key_model, os.path.join(MODEL_DIR, "keystroke_model.pkl"))
    joblib.dump(mouse_model, os.path.join(MODEL_DIR, "mouse_model.pkl"))
    joblib.dump(click_model, os.path.join(MODEL_DIR, "click_model.pkl"))

    joblib.dump(key_scaler, os.path.join(MODEL_DIR, "keystroke_scaler.pkl"))
    joblib.dump(mouse_scaler, os.path.join(MODEL_DIR, "mouse_scaler.pkl"))
    joblib.dump(click_scaler, os.path.join(MODEL_DIR, "click_scaler.pkl"))

    print("[INFO] Models and scalers saved.")

    # ---------------- FUSION THRESHOLD ---------------- #

    print("\n[INFO] Calculating fusion threshold...")

    key_scores = -key_model.decision_function(key_scaled)
    mouse_scores = -mouse_model.decision_function(mouse_scaled)
    click_scores = -click_model.decision_function(click_scaled)

    # 🔥 FIX: Align dataset sizes
    min_length = min(len(key_scores), len(mouse_scores), len(click_scores))

    key_scores = key_scores[:min_length]
    mouse_scores = mouse_scores[:min_length]
    click_scores = click_scores[:min_length]

    combined_scores = np.column_stack((key_scores, mouse_scores, click_scores))

    # Normalize scores to 0–1 range
    fusion_scaler = MinMaxScaler()
    normalized_scores = fusion_scaler.fit_transform(combined_scores)

    final_scores = (
        0.5 * normalized_scores[:, 0] +
        0.3 * normalized_scores[:, 1] +
        0.2 * normalized_scores[:, 2]
    )

    threshold = final_scores.mean() + 2 * final_scores.std()

    joblib.dump(fusion_scaler, os.path.join(MODEL_DIR, "fusion_scaler.pkl"))
    joblib.dump(threshold, os.path.join(MODEL_DIR, "fusion_threshold.pkl"))

    print("[INFO] Fusion threshold calculated:", threshold)

    # ---------------- UPDATE STATE ---------------- #

    state = {
        "mode": "MONITOR",
        "models_trained": True
    }

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

    print("\n[INFO] Training complete.")
    print("[INFO] System switched to MONITOR mode.")


if __name__ == "__main__":
    train_models()