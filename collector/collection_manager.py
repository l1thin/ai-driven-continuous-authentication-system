import threading
import time
import json
import os

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
STATE_FILE = os.path.join(BASE_DIR, "system_state.json")


class CollectionManager:

    def __init__(self):
        self.collection_complete = False

        self.key_thread = threading.Thread(target=start_logger)
        self.mouse_thread = threading.Thread(target=start_mouse_logger)

    def start_collection(self):
        print("[INFO] Unified Collection Mode Started\n")

        self.key_thread.start()
        self.mouse_thread.start()

        self.monitor_thresholds()

    def monitor_thresholds(self):

        while not self.collection_complete:

            time.sleep(5)

            print("\n--- LIVE COUNTS ---")
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