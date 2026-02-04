import csv
import json
import re

CSV_FILE = "de2_115_pin_assignments.csv"
OUT_FILE = "de2_115_pins.json"

# Groups we support in Version-0
SUPPORTED_PREFIXES = ("KEY[", "SW[", "LEDR[", "LEDG[", "CLOCK")

board = {}

def add_bus_entry(bus, index, pin, io):
    if bus not in board:
        board[bus] = {}
    board[bus][index] = {
        "pin": pin,
        "io_standard": io
    }

with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

    header_found = False
    headers = []

    for row in reader:
        if not row:
            continue

        # Skip comments
        if row[0].startswith("#"):
            continue

        # Detect header row
        if not header_found and row[0] == "To":
            headers = row
            header_found = True
            continue

        if not header_found:
            continue

        record = dict(zip(headers, row))

        signal = record["To"].strip()
        location = record["Location"].replace("PIN_", "").strip()
        io_std = record["I/O Standard"].strip()

        # -------- CLOCK --------
        if signal.startswith("CLOCK"):
            board["CLOCK_50"] = {
                "pin": location,
                "io_standard": io_std
            }

        # -------- BUS SIGNALS --------
        elif signal.startswith(SUPPORTED_PREFIXES):
            match = re.match(r"([A-Z]+)\[(\d+)\]", signal)
            if match:
                bus, idx = match.groups()
                add_bus_entry(bus, idx, location, io_std)

# Write JSON
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(board, f, indent=2)

print(f"Generated {OUT_FILE}")
