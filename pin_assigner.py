import sys
import re

def parse_verilog_ports(verilog_path):
    with open(verilog_path, "r") as f:
        text = f.read()

    # Find first module declaration
    module_match = re.search(r"module\s+\w+\s*\((.*?)\);\s*endmodule", text, re.S)
    if not module_match:
        raise RuntimeError("No valid module found")

    port_block = module_match.group(1)

    ports = []
    for line in port_block.split(","):
        line = line.strip()
        if not line:
            continue

        m = re.match(r"(input|output)\s+(\w+)", line)
        if not m:
            raise RuntimeError(f"Unsupported port format: {line}")

        direction, name = m.groups()
        ports.append({
            "name": name,
            "dir": direction
        })

    return ports

def main():
    if len(sys.argv) == 1:

        
        # DEV MODE fallback
        verilog_file = "test_top.v"
        print("[DEV] No file provided, using test_top.v")
    elif len(sys.argv) == 2:
        verilog_file = sys.argv[1]
    else:
        print("Usage: python pin_assigner.py <verilog_file>")
        sys.exit(1)

    ports = parse_verilog_ports(verilog_file)

    print("Parsed ports:")
    for p in ports:
        print(f"  {p['dir']:6} {p['name']}")




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
