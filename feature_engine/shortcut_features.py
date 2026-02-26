import os
import pandas as pd
import numpy as np

WINDOW_SIZE = 60  # seconds

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_FILE = os.path.join(BASE_DIR, "data", "raw", "shortcuts.csv")
FEATURE_DIR = os.path.join(BASE_DIR, "data", "features")
FEATURE_FILE = os.path.join(FEATURE_DIR, "shortcut_features.csv")

if not os.path.exists(FEATURE_DIR):
    os.makedirs(FEATURE_DIR)


def extract_features():

    if not os.path.exists(RAW_FILE):
        print("[INFO] No shortcuts.csv found.")
        return

    df = pd.read_csv(RAW_FILE)

    if df.empty:
        print("[INFO] shortcuts.csv is empty.")
        return

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

        if len(window_df) < 3:
            current_start = current_end
            continue

        total_shortcuts = len(window_df)

        # Modifier counts
        ctrl_count = window_df["shortcut"].str.contains("CTRL").sum()
        alt_count = window_df["shortcut"].str.contains("ALT").sum()
        shift_count = window_df["shortcut"].str.contains("SHIFT").sum()
        win_count = window_df["shortcut"].str.contains("WIN").sum()

        multi_modifier_count = window_df["shortcut"].str.count("\\+").gt(1).sum()

        unique_shortcuts = window_df["shortcut"].nunique()

        # Most frequent shortcut ratio
        top_freq = window_df["shortcut"].value_counts().iloc[0]
        top_ratio = top_freq / total_shortcuts

        feature_rows.append({
            "total_shortcuts": total_shortcuts,
            "shortcut_rate": total_shortcuts / WINDOW_SIZE,
            "ctrl_ratio": ctrl_count / total_shortcuts,
            "alt_ratio": alt_count / total_shortcuts,
            "shift_ratio": shift_count / total_shortcuts,
            "win_ratio": win_count / total_shortcuts,
            "multi_modifier_ratio": multi_modifier_count / total_shortcuts,
            "unique_shortcuts": unique_shortcuts,
            "top_shortcut_ratio": top_ratio
        })

        current_start = current_end

    feature_df = pd.DataFrame(feature_rows)
    feature_df = feature_df.replace([np.inf, -np.inf], np.nan).dropna()

    feature_df.to_csv(FEATURE_FILE, index=False)

    print("[INFO] Shortcut features saved:", FEATURE_FILE)


if __name__ == "__main__":
    extract_features()