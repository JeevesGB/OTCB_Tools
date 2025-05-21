import struct
from pathlib import Path

def read_floats(data, offset, count):
    return struct.unpack_from("<" + "f" * count, data, offset)

def scan_vertices(data, stride=12, max_vertices=10000):
    vertices = []
    for offset in range(0, len(data) - stride, stride):
        try:
            x, y, z = read_floats(data, offset, 3)
            if all(-10000 < v < 10000 for v in (x, y, z)):
                vertices.append((x, y, z))
        except:
            continue
        if len(vertices) >= max_vertices:
            break
    return vertices

def scan_face_indices(data, vertex_count, max_faces=5000):
    faces = []
    for offset in range(0, len(data) - 6, 2):  # 3 indices x 2 bytes
        try:
            a, b, c = struct.unpack_from("<HHH", data, offset)
            if max(a, b, c) < vertex_count and a != b and b != c and a != c:
                faces.append((a + 1, b + 1, c + 1))  # OBJ is 1-indexed
        except:
            continue
        if len(faces) >= max_faces:
            break
    return faces

def export_obj(vertices, faces, output_path):
    with open(output_path, "w") as f:
        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for face in faces:
            f.write(f"f {face[0]} {face[1]} {face[2]}\n")
    print(f"Saved {output_path}")

def extract_model(filepath):
    filepath = Path(filepath)
    data = filepath.read_bytes()

    vertices = scan_vertices(data)
    print(f"Found {len(vertices)} vertices.")

    faces = scan_face_indices(data, len(vertices))
    print(f"Detected {len(faces)} face indices.")

    # Output directory named after the .BIN file
    output_dir = filepath.parent / filepath.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{filepath.stem}.obj"
    export_obj(vertices, faces, output_path)


extract_model("CIRCU_A1.BIN")
