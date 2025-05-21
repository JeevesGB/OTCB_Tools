import struct
from pathlib import Path

def extract_texture_offsets(data, max_entries=256):
    offsets = []
    for i in range(0, max_entries * 4, 4):
        offset = struct.unpack_from("<I", data, i)[0]
        if offset == 0 or offset >= len(data):
            break
        offsets.append(offset)
    return sorted(set(offsets))

def extract_tim_blocks(filepath):
    data = Path(filepath).read_bytes()
    offsets = extract_texture_offsets(data)

    print(f"Found {len(offsets)} texture offsets.")

    output_dir = Path(filepath).with_suffix('')  # e.g., CIRCU_A1/
    output_dir.mkdir(exist_ok=True)

    for i, offset in enumerate(offsets):
        # Attempt to find the end of this block
        end = offsets[i + 1] if i + 1 < len(offsets) else len(data)
        block = data[offset:end]

        out_path = output_dir / f"texture_{i:02}.tim"
        with open(out_path, "wb") as f:
            f.write(block)
        print(f"Saved {out_path}")

# Example usage:
extract_tim_blocks("CIRCU_A1.TIX")
