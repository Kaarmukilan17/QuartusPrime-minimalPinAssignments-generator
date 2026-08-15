# Quartus Prime – Minimal Pin Assignment Generator

A small tool to generate **pin assignment QSF files** for the **Terasic DE2-115** board, directly from a Verilog top module. Built to **avoid manual Pin Planner usage** in Quartus for simple lab designs.

Comes in two forms:

* **Web Edition** — click pins directly on a picture of the board, no install needed
* **CLI Edition** — a Python script for local, scriptable use

---

## Web Edition

**Live here → [kaarmukilan17.github.io/QuartusPrime-minimalPinAssignments-generator](https://kaarmukilan17.github.io/QuartusPrime-minimalPinAssignments-generator/)**

No Python, no install — just open the link.

### How to use it

1. **Paste your Verilog top module** into the text box, or click **Load sample module** to try it with a ready-made example.
2. Click **Start assignment**. This reads every port in your module (including buses like `sw[3:0]`) and lists each individual bit that needs a pin.
3. In the port list, **click a line** (e.g. `sw[3]`) to select it — it highlights, and the board image reacts: any region that's a *valid* target for that port **pulses amber**. Everything that doesn't apply (wrong direction, wrong resource) is dimmed out, so you can't pick something invalid.
4. **Click the amber region on the board image.** A row of buttons appears below the board showing every free pin in that group (e.g. `SW[0]`, `SW[1]`, `SW[2]` …).
5. **Click a button** to assign that exact pin. The port list line turns **green** and shows the assigned pin, and the tool automatically jumps to the next unassigned line.
6. Repeat for every port. Once you're happy, either:
   * **Copy to clipboard**, or
   * **Download design_pins.qsf**

   Both give you the exact same file — the CLI version's output format, generated in the browser.

### What it supports

Same board rules as the CLI tool:

| Port type | What's offered |
|---|---|
| `input` | CLOCK_50, KEY[n], SW[n] |
| `output` | LEDR[n], LEDG[n] always |
| `output`, width = 7 bits | + HEX0–HEX7 segments (unlocked by **width**, not name) |
| `output`, name contains `lcd` | + LCD_DATA / LCD_RS / LCD_RW / LCD_EN / LCD_BLON (unlocked by **name**, not width) |

Both HEX and LCD unlocks are independent — a 7-bit port named `lcd_seg` gets both.

---

## CLI Edition

A Python script for local use — same logic as the web version, run from a terminal.

### Scope

**Supports**

* Single-bit ports and multi-bit buses (`led[3:0]`)
* Directions: `input`, `output`
* Board resources: `CLOCK_50`, `KEY[n]`, `SW[n]`, `LEDR[n]`, `LEDG[n]`, `HEX0`–`HEX7`, `LCD_DATA` + LCD control signals
* Interactive CLI selection, grouped by bus for readability
* Prevents duplicate physical pin usage
* Generates a standalone `design_pins.qsf`
* Parses real modules — ports can have any logic (`always` blocks, `assign` statements) between the port list and `endmodule`

**Does NOT support**

* `inout` ports
* Non-ANSI port declarations (ports declared separately from the header)
* Multi-module parsing (only the first module in the file is read)
* GUI (use the Web Edition for that)
* Timing constraints (`.sdc`)
* Automatic Quartus project creation

### What Must Exist on the Target (Lab) Machine

Inside your Quartus project directory:

```
lab_project/
├─ top.v                 ← Your Verilog top module
├─ lab_project.qpf       ← Quartus project file
├─ de2_115_base.qsf      ← Board + device configuration
```

These usually already exist if the project was created using Quartus for DE2-115.

### What Goes Into the Project (What You Carry)

```
pin-assigner-cli/
├─ pin_assigner.py            ← REQUIRED
├─ de2_115_pins.json          ← REQUIRED
├─ de2_115_pin_assignments.csv← source data, only needed if regenerating the JSON
├─ csv_to_board_json.py       ← regenerates de2_115_pins.json from the CSV, if ever needed
├─ USAGE.md                   ← detailed usage guide
└─ test_top.v                 ← safe stub file for a quick test run
```

**Do NOT copy into your actual Quartus project folder:**

* `.qsf` files from this repo (`de2_115_base.qsf`, `design_pins.qsf`) — those belong to *your* project, not the tool
* `output_files/`, `db/` — Quartus-generated directories

### How to Use

1. Copy `pin_assigner.py` and `de2_115_pins.json` into your Quartus project folder
2. Ensure `de2_115_base.qsf` is present in that folder (from your own project)
3. Run:

   ```
   python pin_assigner.py top.v
   ```
4. Follow the interactive prompts to select board pins
5. A file named `design_pins.qsf` will be generated
6. Compile the project in Quartus — it will merge `design_pins.qsf` with the existing project settings

See `USAGE.md` for the full breakdown of the HEX/LCD unlock rules, used-pin constraints, and port format details.

### Output

The tool generates `design_pins.qsf`, containing only:

* `set_location_assignment`
* `set_instance_assignment` (IO standard)

No existing files are modified.

---

## Version History

* **v0** — Minimal, single-bit pin assignment generator, CLI-based
* **v1** — Added multi-bit (bus) port support; buses expanded into individual bit-level signals
* **v1.1** — Grouped bus signals together in the CLI for readability (no change to generated `.qsf`)
* **v1.2** — Fixed module parsing to support real designs (logic between the port list and `endmodule`), not just empty stub modules
* **Web Edition** — Browser-based version with clickable board image, no install required

Board-specific to DE2-115 throughout. Future versions may add other boards, `inout` support, and non-interactive config mode.