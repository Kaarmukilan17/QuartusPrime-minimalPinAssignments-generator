# Quartus Prime – Minimal Pin Assignment Generator (V0)


Most beginner level works involves these mostly

A small Python tool to generate **pin assignment QSF files** for the **Terasic DE2-115** board, directly from a Verilog top module.
This tool is intended to **avoid manual Pin Planner usage** in Quartus for simple lab designs.

---

## Scope (V0)

**What V0 supports**

* Single-bit ports only
* Directions: `input`, `output`
* Board resources:

  * `CLOCK_50`
  * `KEY[n]`
  * `SW[n]`
  * `LEDR[n]`, `LEDG[n]`
* Interactive CLI selection
* Prevents duplicate physical pin usage
* Generates a standalone `design_pins.qsf`

**What V0 does NOT support**

* No buses (`[3:0]`, `[7:0]`, etc.)
* No multi-module parsing
* No GUI
* No timing constraints (`.sdc`)
* No automatic Quartus project creation

**Assumptions**

* The top module is the **first module** in the Verilog file
* Port declarations are simple (`input clk`, `output led`)

---

## Typical Use Case

* You already have a Quartus project for DE2-115
* You want to quickly assign pins to switches, keys, LEDs, or clock
* You do **not** want to open the Pin Planner GUI

---

## What Must Exist on the Target (Lab) Machine

Inside the Quartus project directory:

```
lab_project/
├─ top.v                 ← Your Verilog top module
├─ lab_project.qpf       ← Quartus project file
├─ de2_115_base.qsf      ← Board + device configuration
```

These usually already exist if the project was created using Quartus for DE2-115.

---

## What Goes Into the ZIP (What You Carry)

When sharing or moving the tool, include **only the tool files**:

```
pin_assigner_v0.zip
└─ pin_assigner_v0/
   ├─ pin_assigner.py        ← REQUIRED
   ├─ de2_115_pins.json     ← REQUIRED
   └─ README.md             ← OPTIONAL
```

**Do NOT include**

* `.qsf` files
* `.qpf` files
* `output_files/`
* `db/`
* Any Quartus-generated directories

---

## How to Use

1. Copy `pin_assigner.py` and `de2_115_pins.json` into your Quartus project folder
2. Ensure `de2_115_base.qsf` is present
3. Run:

   ```
   python pin_assigner.py top.v
   ```
4. Follow the interactive prompts to select board pins
5. A file named `design_pins.qsf` will be generated
6. Compile the project in Quartus

Quartus will merge `design_pins.qsf` with the existing project settings.

---

## Output

The tool generates:

```
design_pins.qsf
```

This file contains only:

* `set_location_assignment`
* `set_instance_assignment` (IO standard)

No existing files are modified.

---

## Version

**v0**

* Minimal, single-bit pin assignment generator
* CLI-based
* Board-specific to DE2-115

Future versions may add:

* Bus handling
* Non-interactive config mode
* GUI / board image selection
