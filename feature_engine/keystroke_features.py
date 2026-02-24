import os
import pandas as pd
import numpy as np

WINDOW_SIZE = 60  # seconds

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_FILE = os.path.join(BASE_DIR, "data", "raw", "keystroke.csv")
FEATURE_DIR = os.path.join(BASE_DIR, "data", "features")
FEATURE_FILE = os.path.join(FEATURE_DIR, "keystroke_features.csv")

if not os.path.exists(FEATURE_DIR):
    os.makedirs(FEATURE_DIR)


def extract_features():

    df = pd.read_csv(RAW_FILE)
    df = df.dropna()

    df = df.sort_values("press_time")

    start_time = df["press_time"].min()
    end_time = df["press_time"].max()

    feature_rows = []
    current_start = start_time

    while current_start < end_time:
        current_end = current_start + WINDOW_SIZE

        window_df = df[
            (df["press_time"] >= current_start) &
            (df["press_time"] < current_end)
        ]

        if len(window_df) < 10:
            current_start = current_end
            continue

        feature_rows.append({
            "mean_hold": window_df["hold_time"].mean(),
            "std_hold": window_df["hold_time"].std(),
            "mean_flight": window_df["flight_time"].mean(),
            "std_flight": window_df["flight_time"].std(),
            "typing_speed": len(window_df) / WINDOW_SIZE
        })

        current_start = current_end

    feature_df = pd.DataFrame(feature_rows)
    feature_df = feature_df.replace([np.inf, -np.inf], np.nan).dropna()
    feature_df.to_csv(FEATURE_FILE, index=False)

    print("[INFO] Keystroke features saved:", FEATURE_FILE)


if __name__ == "__main__":
    extract_features()