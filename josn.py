import json
import os

OPEN_POSITIONS_FILE = "open_positions.json"

def save_open_position(position_data):
    positions = []
    if os.path.exists(OPEN_POSITIONS_FILE):
        with open(OPEN_POSITIONS_FILE, "r") as f:
            positions = json.load(f)
    positions.append(position_data)
    with open(OPEN_POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=4)

def load_open_positions():
    if os.path.exists(OPEN_POSITIONS_FILE):
        with open(OPEN_POSITIONS_FILE, "r") as f:
            return json.load(f)
    return []

def remove_position(symbol):
    positions = load_open_positions()
    positions = [pos for pos in positions if pos['symbol'] != symbol]
    with open(OPEN_POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=4)
