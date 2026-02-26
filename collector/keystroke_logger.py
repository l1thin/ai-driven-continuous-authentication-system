import os
import time
import pandas as pd
from pynput import keyboard
import shared_state

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

last_press_time = None
last_release_time = None

# Modifier states
ctrl_pressed = False
alt_pressed = False
shift_pressed = False
win_pressed = False


def log_shortcut(shortcut_type, timestamp):
    file_path = os.path.join(BASE_DIR, "data", "raw", "shortcuts.csv")

    df = pd.DataFrame([{
        "timestamp": timestamp,
        "shortcut": shortcut_type
    }])

    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, mode="a", header=False, index=False)

    shared_state.shortcut_count += 1
    print("Shortcut detected:", shortcut_type)


def format_key(key):
    """
    Converts pynput key object to clean readable string
    """
    if hasattr(key, "char") and key.char:
        return key.char.upper()
    else:
        return str(key).replace("Key.", "").upper()


def on_press(key):
    global last_press_time
    global ctrl_pressed, alt_pressed, shift_pressed, win_pressed

    current_time = time.time()

    # Track modifier keys
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        ctrl_pressed = True
        return

    if key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
        alt_pressed = True
        return

    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = True
        return

    if key in (keyboard.Key.cmd,):
        win_pressed = True
        return

    # ---- Timing logic ----
    if last_release_time:
        flight_time = current_time - last_release_time
    else:
        flight_time = 0

    last_press_time = current_time

    # ---- Generic Shortcut Detection ----
    modifiers = []

    if ctrl_pressed:
        modifiers.append("CTRL")

    if alt_pressed:
        modifiers.append("ALT")

    if shift_pressed:
        modifiers.append("SHIFT")

    if win_pressed:
        modifiers.append("WIN")

    key_name = format_key(key)

    # Only log if at least one modifier is active
    if modifiers:
        shortcut_type = "+".join(modifiers + [key_name])
        log_shortcut(shortcut_type, current_time)

    shared_state.key_event_count += 1


def on_release(key):
    global last_press_time, last_release_time
    global ctrl_pressed, alt_pressed, shift_pressed, win_pressed

    current_time = time.time()

    # ---- Hold Time Logging ----
    if last_press_time:
        hold_time = current_time - last_press_time
        last_release_time = current_time

        file_path = os.path.join(BASE_DIR, "data", "raw", "keystroke.csv")

        df = pd.DataFrame([{
            "press_time": last_press_time,
            "release_time": current_time,
            "hold_time": hold_time,
            "flight_time": hold_time
        }])

        if not os.path.exists(file_path):
            df.to_csv(file_path, index=False)
        else:
            df.to_csv(file_path, mode="a", header=False, index=False)

        shared_state.hold_count += 1
        shared_state.flight_count += 1

    # ---- Reset Modifiers ----
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        ctrl_pressed = False

    if key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
        alt_pressed = False

    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = False

    if key in (keyboard.Key.cmd,):
        win_pressed = False

    if shared_state.stop_collection:
        return False


def start_logger():
    print("[INFO] Keystroke logger started with FULL shortcut tracking...")

    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    ) as listener:
        listener.join()