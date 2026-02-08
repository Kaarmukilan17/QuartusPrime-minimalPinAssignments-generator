import csv
import json
import re

CSV_FILE = "de2_115_pin_assignments.csv"
OUT_FILE = "de2_115_pins.json"

# All supported bus-style prefixes
SUPPORTED_BUS_PREFIXES = (
    "KEY",
    "SW",
    "LEDR",
    "LEDG",
    "HEX",
    "LCD_DATA",
)

board = {}


def add_bus_entry(bus, index, pin, io):
    """Add a bus[index] entry into board dict"""
    if bus not in board:
        board[bus] = {}

    board[bus][str(index)] = {
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
        if not header_found and row[0].strip() == "To":
            headers = [h.strip() for h in row]
            header_found = True
            continue

        if not header_found:
            continue

        record = dict(zip(headers, row))

        signal = record["To"].strip()
        location = record["Location"].replace("PIN_", "").strip()
        io_std = record["I/O Standard"].strip()

        # ---------------- CLOCK ----------------
        if signal.startswith("CLOCK"):
            board["CLOCK_50"] = {
                "pin": location,
                "io_standard": io_std
            }
            continue

        # ---------------- LCD CONTROL ----------------
        if signal in ("LCD_RS", "LCD_RW", "LCD_EN", "LCD_BLON", "LCD_ON"):
            board[signal] = {
                "pin": location,
                "io_standard": io_std
            }
            continue

        # ---------------- BUS SIGNALS ----------------
        # Matches: KEY[3], SW[0], LEDR[17], HEX0[6], LCD_DATA[7]
        match = re.match(r"([A-Z_]+\d*)\[(\d+)\]", signal)
        if match:
            bus, idx = match.groups()

            # Only accept supported buses
            if bus.startswith(SUPPORTED_BUS_PREFIXES):
                add_bus_entry(bus, idx, location, io_std)

# Write output JSON
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(board, f, indent=2)

print(f"✅ Generated {OUT_FILE}")
