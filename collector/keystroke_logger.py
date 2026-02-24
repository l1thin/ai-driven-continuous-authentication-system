import os
import time
import pandas as pd
from pynput import keyboard
from collector import shared_state

# ---------------- PATH SETUP ---------------- #

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
KEY_FILE = os.path.join(RAW_DIR, "keystroke.csv")

if not os.path.exists(RAW_DIR):
    os.makedirs(RAW_DIR)

if not os.path.exists(KEY_FILE):
    pd.DataFrame(columns=[
        "key",
        "press_time",
        "release_time",
        "hold_time",
        "flight_time"
    ]).to_csv(KEY_FILE, index=False)

# ---------------- STATE ---------------- #

key_press_times = {}
last_release_time = None


def on_press(key):
    if shared_state.stop_collection:
        return False

    global key_press_times

    try:
        k = key.char
    except AttributeError:
        k = str(key)

    with shared_state.lock:
        key_press_times[k] = time.time()
        shared_state.key_event_count += 1


def on_release(key):
    if shared_state.stop_collection:
        return False

    global last_release_time

    try:
        k = key.char
    except AttributeError:
        k = str(key)

    with shared_state.lock:
        if k in key_press_times:
            press_time = key_press_times.pop(k)
            release_time = time.time()
            hold_time = release_time - press_time

            shared_state.hold_count += 1

            if last_release_time is not None:
                flight_time = press_time - last_release_time
                shared_state.flight_count += 1
            else:
                flight_time = 0

            last_release_time = release_time

            row = {
                "key": k,
                "press_time": press_time,
                "release_time": release_time,
                "hold_time": hold_time,
                "flight_time": flight_time
            }

            pd.DataFrame([row]).to_csv(
                KEY_FILE,
                mode="a",
                header=False,
                index=False
            )


def start_logger():
    print("[INFO] Keystroke logger started...")

    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    ) as listener:
        listener.join()