from pathlib import Path

def hex_dump(filepath, count=512):
    data = Path(filepath).read_bytes()
    chunk = data[:count]
    hex_lines = []
    for i in range(0, len(chunk), 16):
        hex_chunk = " ".join(f"{b:02X}" for b in chunk[i:i+16])
        ascii_chunk = "".join(chr(b) if 32 <= b <= 126 else '.' for b in chunk[i:i+16])
        hex_lines.append(f"{i:08X}  {hex_chunk:<47}  {ascii_chunk}")
    return "\n".join(hex_lines)

dump = hex_dump(r"C:\Users\there\Desktop\OTCB Tools\track extraction\Track .bin\TOUGE_C1.BIN")
print(dump)
