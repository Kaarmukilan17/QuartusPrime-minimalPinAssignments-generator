import csv
import json
import re

CSV_FILE = "de2_115_pin_assignments.csv"
OUT_FILE = "de2_115_pins.json"

# Groups supported
SUPPORTED_PREFIXES = (
    "KEY[", "SW[", "LEDR[", "LEDG[",
    "HEX",        # HEX0–HEX7
    "CLOCK"
)

board = {}

def add_bus_entry(bus, index, pin, io):
    if bus not in board:
        board[bus] = {}
    board[bus][str(index)] = {
        "pin": pin,
        "io_standard": io
    }

lcd_data_index = 7  # LCD_DATA[7:0]

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

        # Detect header
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

        # -------- LCD DATA (bus) --------
        elif signal == "LCD_DATA":
            add_bus_entry("LCD_DATA", lcd_data_index, location, io_std)
            lcd_data_index -= 1

        # -------- LCD CONTROL --------
        elif signal in ("LCD_RS", "LCD_RW", "LCD_EN", "LCD_BLON"):
            board[signal] = {
                "pin": location,
                "io_standard": io_std
            }

        # -------- BUS SIGNALS (KEY, SW, LEDR, LEDG, HEXx) --------
        elif signal.startswith(SUPPORTED_PREFIXES):
            match = re.match(r"([A-Z]+\d*)\[(\d+)\]", signal)
            if match:
                bus, idx = match.groups()
                add_bus_entry(bus, idx, location, io_std)

# Write JSON
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(board, f, indent=2)

print(f"Generated {OUT_FILE}")
