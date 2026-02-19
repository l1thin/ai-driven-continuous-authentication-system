import pandas as pd
import numpy as np
import glob
import os

DATA_FOLDER = "./data"
WINDOW_SIZE = 30
OUTPUT_FILE = "final_ml_dataset.csv"

def extract_features(filepath, label):

    print(f"Processing {os.path.basename(filepath)} | Label: {label}")

    df = pd.read_csv(filepath)
    df.rename(columns={"key_dwell_ms": "key_dwell"}, inplace=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

# Convert to seconds from start of session
    df["time_seconds"] = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds()

# Create window
    df["window"] = (df["time_seconds"] // WINDOW_SIZE)


    # Mouse movement
    df["dx"] = df["mouse_x"].diff()
    df["dy"] = df["mouse_y"].diff()
    df["dt"] = df["time_seconds"].diff()


    df["distance"] = np.sqrt(df["dx"]**2 + df["dy"]**2)
    df["mouse_speed"] = df["distance"] / df["dt"]
    df["mouse_acceleration"] = df["mouse_speed"].diff() / df["dt"]

    df["scroll_intensity"] = np.sqrt(df["scroll_dx"]**2 + df["scroll_dy"]**2)

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)

    # Aggregate window features
    features = df.groupby("window").agg({

        # Keyboard
        "key_dwell": ["mean", "std", "min", "max"],

        # Mouse
        "mouse_speed": ["mean", "std"],
        "mouse_acceleration": ["mean", "std"],
        "distance": ["sum"],

        # Scroll
        "scroll_intensity": ["mean", "std"],

        # Idle
        "idle_seconds": ["mean", "max"],

        # Event count
        "event_type": "count"
    })

    features.columns = [
        "_".join(col) for col in features.columns
    ]

    features = features.reset_index(drop=True)
    features["label"] = label

    return features


def build_dataset():

    all_files = glob.glob(os.path.join(DATA_FOLDER, "*.csv"))

    all_features = []

    for file in all_files:

        filename = os.path.basename(file)

        if "intruder" in filename.lower():
            label = 1   # Intruder
        else:
            label = 0   # Genuine user

        features = extract_features(file, label)
        all_features.append(features)

    final_df = pd.concat(all_features, ignore_index=True)
    final_df.to_csv(OUTPUT_FILE, index=False)

    print("\n✅ Dataset created successfully")
    print("Shape:", final_df.shape)


if __name__ == "__main__":
    build_dataset()
