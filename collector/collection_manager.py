import threading
import time
import json
import os
import pandas as pd

from keystroke_logger import start_logger
from mouse_logger import start_mouse_logger
import shared_state

KEY_THRESHOLD = 45000
HOLD_THRESHOLD = 45000
FLIGHT_THRESHOLD = 45000

MOVE_THRESHOLD = 100000
CLICK_THRESHOLD = 1500

SHORTCUT_THRESHOLD = 800

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
STATE_FILE = os.path.join(BASE_DIR, "system_state.json")


class CollectionManager:

    def __init__(self):
        self.collection_complete = False
        self.key_thread = threading.Thread(target=start_logger)
        self.mouse_thread = threading.Thread(target=start_mouse_logger)

    def initialize_counters_from_files(self):

        key_file = os.path.join(RAW_DIR, "keystroke.csv")
        move_file = os.path.join(RAW_DIR, "mouse_move.csv")
        click_file = os.path.join(RAW_DIR, "mouse_click.csv")
        shortcut_file = os.path.join(RAW_DIR, "shortcuts.csv")

        if os.path.exists(key_file):
            df = pd.read_csv(key_file)
            shared_state.key_event_count = len(df)
            shared_state.hold_count = len(df)
            shared_state.flight_count = len(df)

        if os.path.exists(move_file):
            shared_state.move_count = len(pd.read_csv(move_file))

        if os.path.exists(click_file):
            shared_state.click_count = len(pd.read_csv(click_file))

        if os.path.exists(shortcut_file):
            shared_state.shortcut_count = len(pd.read_csv(shortcut_file))

    def start_collection(self):
        print("\n[INFO] Collection Mode Started\n")

        self.initialize_counters_from_files()

        self.key_thread.start()
        self.mouse_thread.start()

        self.monitor_thresholds()

    def monitor_thresholds(self):

        while not self.collection_complete:
            time.sleep(10)

            print("\n==============================")
            print("📊 LIVE CUMULATIVE PROGRESS")
            print("==============================")
            print(f"Keys: {shared_state.key_event_count} / {KEY_THRESHOLD}")
            print(f"Moves: {shared_state.move_count} / {MOVE_THRESHOLD}")
            print(f"Clicks: {shared_state.click_count} / {CLICK_THRESHOLD}")
            print(f"Shortcuts: {shared_state.shortcut_count} / {SHORTCUT_THRESHOLD}")
            print("==============================")

            if (
                shared_state.key_event_count >= KEY_THRESHOLD and
                shared_state.move_count >= MOVE_THRESHOLD and
                shared_state.click_count >= CLICK_THRESHOLD and
                shared_state.shortcut_count >= SHORTCUT_THRESHOLD
            ):
                self.collection_complete = True

        print("\n🔥 Profile Collection Completed.")
        shared_state.stop_collection = True
        time.sleep(2)
        self.update_state()

    def update_state(self):
        state = {
            "mode": "TRAIN",
            "models_trained": False
        }

        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)

        print("[INFO] System state updated → TRAIN mode")


if __name__ == "__main__":
    manager = CollectionManager()
    manager.start_collection()