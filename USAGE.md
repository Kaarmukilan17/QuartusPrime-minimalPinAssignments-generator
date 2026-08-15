

# Pin Assigner – Usage Guide

This tool parses a Verilog top module, interactively maps its ports to DE2-115 board pins, and generates a Quartus `.qsf` file with location and I/O standard assignments.

---

## 1. How to Run

```bash
python pin_assigner.py <top_module.v>
```

If no file is provided, the tool defaults to `test_top.v` (development mode).

---

## 2. Supported Verilog Ports

* Only the **first (top) module** in the file is parsed
* Supported declarations:

  ```verilog
  input  a;
  output b;
  output [6:0] seg;
  ```
* Limitations:

  * No `inout`
  * No multidimensional buses
  * No parameters inside port list

---

## 3. Board Database Requirement

The following file **must exist** in the same directory:

```
de2_115_pins.json
```

This file is generated from the official DE2-115 pin CSV and defines all valid board pins and I/O standards.

---

## 4. Input Port Behavior

For **all input ports**, regardless of width or name, the tool shows **only**:

```
CLOCK_50
KEY[*]
SW[*]
```

The following are **never shown** for inputs:

```
LEDR / LEDG / HEX / LCD
```

---

## 5. Output Port Behavior (Default)

For **all output ports**, the tool always starts by showing:

```
LEDR[*]
LEDG[*]
```

This is the default and always available option set.

---

## 6. HEX Display Unlock (Width-Based)

If an **output bus has width = 7 bits** (`[6:0]`):

```
HEX0[*] … HEX7[*]
```

are added to the selection options.

This rule depends **only on bus width**, not on signal name.

---

## 7. LCD Unlock (Name-Based)

If an **output port name contains `lcd`** (case-insensitive), the following are added:

```
LCD_DATA[*]
LCD_RS
LCD_RW
LCD_EN
LCD_BLON
```

LCD availability depends **only on the signal name**, not on width.

---

## 8. Priority Rule

HEX and LCD rules are **independent**.

If both conditions apply, **both sets are shown** in addition to LEDs.

Example:

```verilog
output [6:0] lcd_seg;
```

Options shown:

```
LEDR[*], LEDG[*], HEX*, LCD*
```

---

## 9. Used-Pin Constraint

* Each board pin can be used **only once**
* Previously assigned pins are automatically removed from later choices

---

## 10. Output File

The tool generates:

```
design_pins.qsf
```

Containing:

* `set_location_assignment`
* `set_instance_assignment -name IO_STANDARD`

This file can be **sourced or merged** into an existing Quartus project.

---

## 11. What This Tool Does NOT Do

* Does not modify `.qpf`
* Does not auto-detect top module in Quartus
* Does not validate functional correctness
* Does not handle timing constraints (`.sdc`)

---

## 12. Intended Use

* Educational labs
* Rapid prototyping
* Teaching pin planning concepts
* Reducing manual Pin Planner errors

---

This behavior is **fully deterministic** and defined entirely by:

* Port direction
* Port width
* Port name
* Board database
