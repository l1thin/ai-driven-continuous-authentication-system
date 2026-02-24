import os
import time
import pandas as pd
from pynput import mouse
import shared_state

# ---------------- PATH SETUP ---------------- #

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

MOVE_FILE = os.path.join(RAW_DIR, "mouse_move.csv")
CLICK_FILE = os.path.join(RAW_DIR, "mouse_click.csv")

if not os.path.exists(RAW_DIR):
    os.makedirs(RAW_DIR)

if not os.path.exists(MOVE_FILE):
    pd.DataFrame(columns=[
        "timestamp",
        "x",
        "y",
        "velocity",
        "acceleration"
    ]).to_csv(MOVE_FILE, index=False)

if not os.path.exists(CLICK_FILE):
    pd.DataFrame(columns=[
        "timestamp",
        "button",
        "interval"
    ]).to_csv(CLICK_FILE, index=False)

# ---------------- STATE ---------------- #

last_position = None
last_time = None
last_velocity = 0
last_click_time = None


def on_move(x, y):
    if shared_state.stop_collection:
        return False

    global last_position, last_time, last_velocity

    current_time = time.time()

    with shared_state.lock:
        if last_position is not None and last_time is not None:
            dx = x - last_position[0]
            dy = y - last_position[1]

            dt = current_time - last_time
            if dt == 0:
                return

            distance = (dx**2 + dy**2) ** 0.5
            velocity = distance / dt
            acceleration = (velocity - last_velocity) / dt

            row = {
                "timestamp": current_time,
                "x": x,
                "y": y,
                "velocity": velocity,
                "acceleration": acceleration
            }

            pd.DataFrame([row]).to_csv(
                MOVE_FILE,
                mode="a",
                header=False,
                index=False
            )

            last_velocity = velocity
            shared_state.move_count += 1

        last_position = (x, y)
        last_time = current_time


def on_click(x, y, button, pressed):
    if shared_state.stop_collection:
        return False

    global last_click_time

    if pressed:
        current_time = time.time()

        with shared_state.lock:
            if last_click_time is not None:
                interval = current_time - last_click_time
            else:
                interval = 0

            last_click_time = current_time

            row = {
                "timestamp": current_time,
                "button": str(button),
                "interval": interval
            }

            pd.DataFrame([row]).to_csv(
                CLICK_FILE,
                mode="a",
                header=False,
                index=False
            )

            shared_state.click_count += 1


def start_mouse_logger():
    print("[INFO] Mouse logger started...")

    with mouse.Listener(
        on_move=on_move,
        on_click=on_click
    ) as listener:
        listener.join()