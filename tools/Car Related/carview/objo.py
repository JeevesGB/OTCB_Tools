def export_obj(path, geometry):
    with open(path, "w") as f:
        for v in geometry.vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for a, b, c in geometry.faces:
            f.write(f"f {a+1} {b+1} {c+1}\n")

def import_obj(path):
    vertices = []
    faces = []

    with open(path) as f:
        for line in f:
            if line.startswith("v "):
                _, x, y, z = line.split()
                vertices.append((float(x), float(y), float(z)))
            elif line.startswith("f "):
                idx = [int(i)-1 for i in line.split()[1:4]]
                faces.append(tuple(idx))

    return vertices, faces