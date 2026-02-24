import threading
import time
import json
import os
import pandas as pd

from keystroke_logger import start_logger
from mouse_logger import start_mouse_logger
import shared_state

# ---------------- THRESHOLDS ---------------- #

KEY_THRESHOLD = 5000
HOLD_THRESHOLD = 1000
FLIGHT_THRESHOLD = 1000
MOVE_THRESHOLD = 10000
CLICK_THRESHOLD = 500

# -------------------------------------------- #

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
STATE_FILE = os.path.join(BASE_DIR, "system_state.json")


class CollectionManager:

    def __init__(self):
        self.collection_complete = False

        self.key_thread = threading.Thread(target=start_logger)
        self.mouse_thread = threading.Thread(target=start_mouse_logger)

    # --------------------------------------------------
    # 🔥 OPTION B — Initialize counters from CSV files
    # --------------------------------------------------

    def initialize_counters_from_files(self):

        key_file = os.path.join(RAW_DIR, "keystroke.csv")
        move_file = os.path.join(RAW_DIR, "mouse_move.csv")
        click_file = os.path.join(RAW_DIR, "mouse_click.csv")

        # Initialize keystroke counters
        if os.path.exists(key_file):
            df_key = pd.read_csv(key_file)
            shared_state.key_event_count = len(df_key)
            shared_state.hold_count = len(df_key)
            shared_state.flight_count = len(df_key)

        # Initialize mouse movement counter
        if os.path.exists(move_file):
            df_move = pd.read_csv(move_file)
            shared_state.move_count = len(df_move)

        # Initialize click counter
        if os.path.exists(click_file):
            df_click = pd.read_csv(click_file)
            shared_state.click_count = len(df_click)

        print("\n[INFO] Initialized counters from existing dataset:")
        print("Keys:", shared_state.key_event_count)
        print("Holds:", shared_state.hold_count)
        print("Flights:", shared_state.flight_count)
        print("Moves:", shared_state.move_count)
        print("Clicks:", shared_state.click_count)

    # --------------------------------------------------

    def start_collection(self):

        print("\n[INFO] Unified Collection Mode Started\n")

        # 🔥 Initialize counters from previous data
        self.initialize_counters_from_files()

        # Start loggers
        self.key_thread.start()
        self.mouse_thread.start()

        # Monitor thresholds
        self.monitor_thresholds()

    # --------------------------------------------------

    def monitor_thresholds(self):

        while not self.collection_complete:

            time.sleep(5)

            print("\n--- LIVE COUNTS (CUMULATIVE) ---")
            print("Keys:", shared_state.key_event_count)
            print("Holds:", shared_state.hold_count)
            print("Flights:", shared_state.flight_count)
            print("Moves:", shared_state.move_count)
            print("Clicks:", shared_state.click_count)

            if (
                shared_state.key_event_count >= KEY_THRESHOLD and
                shared_state.hold_count >= HOLD_THRESHOLD and
                shared_state.flight_count >= FLIGHT_THRESHOLD and
                shared_state.move_count >= MOVE_THRESHOLD and
                shared_state.click_count >= CLICK_THRESHOLD
            ):
                self.collection_complete = True

        print("\n[INFO] ALL DATA THRESHOLDS REACHED.")
        shared_state.stop_collection = True

        # Wait briefly to allow threads to exit cleanly
        time.sleep(2)

        self.update_state()

    # --------------------------------------------------

    def update_state(self):

        state = {
            "mode": "TRAIN",
            "models_trained": False
        }

        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)

        print("[INFO] System state updated → TRAIN mode")


# ------------------------------------------------------

if __name__ == "__main__":
    manager = CollectionManager()
    manager.start_collection()