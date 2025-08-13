import struct
from pathlib import Path

def extract_track_vertices_single(bin_path, out_dir):
    bin_path = Path(bin_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = bin_path.read_bytes()
    filesize = len(data)

    # Read first 16 32-bit LE integers (pointer table)
    header = struct.unpack_from("<16I", data, 0)
    offsets = [off for off in header if 32 < off < filesize - 32]

    print(f"[INFO] {bin_path.name}: header offsets -> {offsets}")

    all_vertices = []
    for off in offsets:
        try:
            count = struct.unpack_from("<I", data, off)[0]
        except struct.error:
            continue

        # Heuristic: plausible vertex count
        if 0 < count <= 200000:
            start = off + 32  # skip ~8 ints (block header)
            end = start + count * 6  # each vertex = 3 × int16
            if end <= filesize:
                triples = struct.unpack_from(f"<{count*3}h", data, start)
                verts = [
                    (triples[i] / 4096.0, triples[i+1] / 4096.0, triples[i+2] / 4096.0)
                    for i in range(0, len(triples), 3)
                ]
                all_vertices.extend(verts)

    # Write single OBJ
    obj_path = out_dir / f"{bin_path.stem}.obj"
    with open(obj_path, "w") as f:
        f.write(f"# Extracted from {bin_path.name} (vertices only)\n")
        for x, y, z in all_vertices:
            f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")

    print(f"[DONE] Wrote {obj_path.name} with {len(all_vertices)} vertices.")

if __name__ == "__main__":
    # Example usage:
    # Place your .BIN files in the same folder as this script, then run:
    # Output OBJ files will be in ./output/
    input_files = [
        "CIRCU_A1.BIN",
        "EBISU_A3.BIN"
    ]
    for file in input_files:
        if Path(file).exists():
            extract_track_vertices_single(file, "output")
        else:
            print(f"[WARN] File not found: {file}")
