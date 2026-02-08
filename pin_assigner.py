import sys
import re
import json

#for grouping ports by bus name (e.g. SW[0], SW[1] -> SW)
from collections import OrderedDict


def parse_verilog_ports(verilog_path):
    with open(verilog_path, "r") as f:
        text = f.read()

    module_match = re.search(
        r"module\s+\w+\s*\((.*?)\);\s*endmodule",
        text,
        re.S
    )
    if not module_match:
        raise RuntimeError("No valid module found")

    port_block = module_match.group(1)

    ports = []
    for line in port_block.split(","):
        line = line.strip()
        if not line:
            continue

        m = re.match(
            r"(input|output)\s*(?:\[\s*(\d+)\s*:\s*(\d+)\s*\]\s*)?(\w+)",
            line
        )
        if not m:
            raise RuntimeError(f"Unsupported port format: {line}")

        direction, msb, lsb, name = m.groups()

        if msb is None:
            msb = lsb = 0
        else:
            msb = int(msb)
            lsb = int(lsb)

        ports.append({
            "name": name,
            "dir": direction,
            "msb": msb,
            "lsb": lsb
        })

    return ports

def expand_ports(ports):
    expanded = []

    for p in ports:
        # Single-bit signal
        if p["msb"] == p["lsb"]:
            expanded.append({
                "name": p["name"],
                "base": p["name"],
                "index": None,
                "dir": p["dir"]
            })
        else:
            # Bus: expand MSB -> LSB
            step = -1 if p["msb"] > p["lsb"] else 1
            for i in range(p["msb"], p["lsb"] + step, step):
                expanded.append({
                    "name": f"{p['name']}[{i}]",
                    "base": p["name"],
                    "index": i,
                    "dir": p["dir"]
                })

    return expanded



def group_ports_by_bus(expanded_ports):
    buses = OrderedDict()

    for p in expanded_ports:
        base = p["base"]

        if base not in buses:
            buses[base] = {
                "dir": p["dir"],
                "bits": []
            }

        buses[base]["bits"].append(p)

    return buses




def load_board_db(json_path="de2_115_pins.json"):
    with open(json_path, "r") as f:
        return json.load(f)

def get_choices_for_port(port, board_db):
    choices = []

    # -------- INPUT PORTS --------
    if port["dir"] == "input":
        if "CLOCK_50" in board_db:
            choices.append("CLOCK_50")

        for group in ("KEY", "SW"):
            if group in board_db:
                for idx in board_db[group]:
                    choices.append(f"{group}[{idx}]")

    # -------- OUTPUT PORTS --------
    elif port["dir"] == "output":
        # LEDs
        for group in ("LEDR", "LEDG"):
            if group in board_db:
                for idx in board_db[group]:
                    choices.append(f"{group}[{idx}]")

        # HEX displays
        for hx in range(8):
            key = f"HEX{hx}"
            if key in board_db:
                for idx in board_db[key]:
                    choices.append(f"{key}[{idx}]")

        # LCD data bus
        if "LCD_DATA" in board_db:
            for idx in board_db["LCD_DATA"]:
                choices.append(f"LCD_DATA[{idx}]")

        # LCD control signals
        for sig in ("LCD_RS", "LCD_RW", "LCD_EN", "LCD_BLON"):
            if sig in board_db:
                choices.append(sig)

    return choices

def prompt_user_for_mapping(ports, board_db):
    mapping = {}
    used = set()

    for port in ports:
        choices = get_choices_for_port(port, board_db)

        print(f"\nPort: {port['name']} ({port['dir']})")

        # filter already-used choices
        filtered = [c for c in choices if c not in used]

        for i, choice in enumerate(filtered):
            print(f"  {i+1}) {choice}")

        while True:
            try:
                sel = int(input("Select option number: "))
                if 1 <= sel <= len(filtered):
                    selected = filtered[sel - 1]
                    mapping[port["name"]] = selected
                    used.add(selected)
                    break
                else:
                    print("Invalid selection. Try again.")
            except ValueError:
                print("Please enter a number.")

    return mapping
# Alternative mapping function that groups ports by bus name (e.g. SW[0], SW[1] -> SW)
def prompt_user_for_mapping_grouped(buses, board_db):
    mapping = {}
    used = set()

    for bus_name, bus in buses.items():
        bits = bus["bits"]
        dirn = bus["dir"]

        if len(bits) > 1:
            msb = bits[0]["index"]
            lsb = bits[-1]["index"]
            print(f"\nBus: {bus_name}[{msb}:{lsb}] ({dirn})")
        else:
            print(f"\nSignal: {bus_name} ({dirn})")

        for bit in bits:
            choices = get_choices_for_port(bit, board_db)
            filtered = [c for c in choices if c not in used]

            print(f"\n  {bit['name']}:")

            for i, choice in enumerate(filtered):
                print(f"    {i+1}) {choice}")

            while True:
                try:
                    sel = int(input("    Select option number: "))
                    if 1 <= sel <= len(filtered):
                        selected = filtered[sel - 1]
                        mapping[bit["name"]] = selected
                        used.add(selected)
                        break
                    else:
                        print("    Invalid selection.")
                except ValueError:
                    print("    Enter a number.")

    return mapping

def write_qsf(mapping, board_db, out_file="design_pins.qsf"):
    with open(out_file, "w") as f:
        f.write("# Auto-generated by pin_assigner.py\n\n")

        for port, board_sig in mapping.items():

            # Handle signals like KEY[3], LEDR[17]
            if "[" in board_sig:
                group, idx = board_sig[:-1].split("[")
                entry = board_db[group][idx]
            else:
                entry = board_db[board_sig]

            pin = entry["pin"]
            ios = entry["io_standard"]

            f.write(f"set_location_assignment PIN_{pin} -to {port}\n")
            #f.write(f"set_location_assignment {pin} -to {port}\n")
            f.write(
                f"set_instance_assignment -name IO_STANDARD \"{ios}\" -to {port}\n\n"
            )
    


def main():
    # Handle command-line arguments
    if len(sys.argv) == 1:

        
        # DEV MODE fallback
        verilog_file = "test_top.v"
        print("[DEV] No file provided, using test_top.v")
    elif len(sys.argv) == 2:
        verilog_file = sys.argv[1]
    else:
        print("Usage: python pin_assigner.py <verilog_file>")
        sys.exit(1)


# Parse ports and load board database
    ports = parse_verilog_ports(verilog_file)
    
    expanded_ports = expand_ports(ports)
    board_db = load_board_db()


    buses = group_ports_by_bus(expanded_ports)
    mapping = prompt_user_for_mapping_grouped(buses, board_db)


    print("\nFinal mapping:")
    for k, v in mapping.items():
        print(f"  {k} -> {v}")

    write_qsf(mapping, board_db)
    print("\nGenerated design_pins.qsf")

    # Debug: print parsed ports
   # print(parse_verilog_ports("test_top.v"))


'''
def main():
    if len(sys.argv) != 2:
        print("Usage: python pin_assigner.py <verilog_file>")
        sys.exit(1)

    verilog_file = sys.argv[1]
    ports = parse_verilog_ports(verilog_file)

    print("Parsed ports:")
    for p in ports:
        print(f"  {p['dir']:6} {p['name']}")
'''


if __name__ == "__main__":
    main()