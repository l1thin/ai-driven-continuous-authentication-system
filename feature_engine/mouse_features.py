import os
import pandas as pd
import numpy as np

WINDOW_SIZE = 60

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_FILE = os.path.join(BASE_DIR, "data", "raw", "mouse_move.csv")
FEATURE_DIR = os.path.join(BASE_DIR, "data", "features")
FEATURE_FILE = os.path.join(FEATURE_DIR, "mouse_features.csv")

if not os.path.exists(FEATURE_DIR):
    os.makedirs(FEATURE_DIR)


def extract_features():

    df = pd.read_csv(RAW_FILE)
    df = df.dropna()
    df = df.sort_values("timestamp")

    start_time = df["timestamp"].min()
    end_time = df["timestamp"].max()

    feature_rows = []
    current_start = start_time

    while current_start < end_time:
        current_end = current_start + WINDOW_SIZE

        window_df = df[
            (df["timestamp"] >= current_start) &
            (df["timestamp"] < current_end)
        ]

        if len(window_df) < 20:
            current_start = current_end
            continue

        feature_rows.append({
            "mean_velocity": window_df["velocity"].mean(),
            "std_velocity": window_df["velocity"].std(),
            "mean_acceleration": window_df["acceleration"].mean(),
            "std_acceleration": window_df["acceleration"].std(),
            "movement_density": len(window_df) / WINDOW_SIZE
        })

        current_start = current_end

    feature_df = pd.DataFrame(feature_rows)
    feature_df = feature_df.replace([np.inf, -np.inf], np.nan).dropna()
    feature_df.to_csv(FEATURE_FILE, index=False)

    print("[INFO] Mouse features saved:", FEATURE_FILE)


if __name__ == "__main__":
    extract_features()