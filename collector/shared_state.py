import threading

lock = threading.Lock()

# Keystroke counters
key_event_count = 0
hold_count = 0
flight_count = 0

# Mouse counters
move_count = 0
click_count = 0

# Stop signal
stop_collection = False