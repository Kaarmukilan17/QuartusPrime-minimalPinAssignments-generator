# FINAL USAGE RULES
These rules completely define how the CLI behaves.

---

### INPUT ports

Always show **only**:

```
CLOCK_50
KEY[*]
SW[*]
```

Never show:

```
LEDR / LEDG / HEX / LCD
```

---

### OUTPUT ports — default behavior

For **any output port** (single-bit or bus):

Show **only**:

```
LEDR[*]
LEDG[*]
```

This keeps the UI simple and familiar.

---

### OUTPUT ports — HEX (size-based unlock)

If **output bus width = 7 bits** (`[6:0]`):

In addition to LEDs, also show:

```
HEX0[*] … HEX7[*]
```

This rule applies **only to HEX** and is purely size-based.

---

### OUTPUT ports — LCD (name-based unlock)

If the **Verilog port name contains `lcd` or `LCD`** (case-insensitive):

In addition to LEDs, also show:

```
LCD_DATA[*]
LCD_RS
LCD_RW
LCD_EN
LCD_BLON
```

⚠ LCD availability depends **only on the signal name**,
❌ NOT on bus size.

Examples that unlock LCD:

```verilog
output lcd_data;
output LCD_CTRL;
output my_lcd_bus;
```

---

### Priority rule (important)

If both apply:

* Name contains `lcd`
* Width is 7 or 8

👉 **Both LED + HEX/LCD options are shown**

No mutual exclusion.


##  EXACT BEHAVIOR SUMMARY (NO AMBIGUITY)

| Verilog port           | Options shown           |
| ---------------------- | ----------------------- |
| `input x`              | CLOCK, KEY, SW          |
| `output led`           | LEDR, LEDG              |
| `output [6:0] seg`     | LEDR, LEDG, HEXx        |
| `output [7:0] data`    | LEDR, LEDG              |
| `output lcd_data`      | LEDR, LEDG, LCD_*       |
| `output [7:0] lcd_bus` | LEDR, LEDG, LCD_*       |
| `output [6:0] lcd_seg` | LEDR, LEDG, HEXx, LCD_* |

---