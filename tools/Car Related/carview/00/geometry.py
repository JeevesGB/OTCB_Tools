from dataclasses import dataclass

@dataclass
class Vertex:
    x: int
    y: int
    z: int

@dataclass
class Face:
    indices: list

def scan_for_vertices(bf: BinaryFile):
    vertices = []

    for o in range(0, len(bf.data) - 8, 2):
        x = bf.s16(o)
        y = bf.s16(o+2)
        z = bf.s16(o+4)

        # Heuristic: PS1-scale coordinates
        if -32768 < x < 32768 and -32768 < y < 32768 and -32768 < z < 32768:
            vertices.append((o, Vertex(x, y, z)))

    return vertices

def scan_for_faces(bf: BinaryFile, max_index=5000):
    faces = []

    for o in range(0, len(bf.data) - 8, 2):
        count = bf.u8(o)
        if 3 <= count <= 4:
            indices = []
            valid = True

            for i in range(count):
                idx = bf.u16(o+1+i*2)
                if idx > max_index:
                    valid = False
                    break
                indices.append(idx)

            if valid:
                faces.append((o, Face(indices)))

    return faces