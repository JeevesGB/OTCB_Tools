import struct

FIXED_SHIFT = 12  # PS1 often uses 12.4 or 16.16 – tweak later

def fixed_to_float(val):
    return val / (1 << FIXED_SHIFT)

class Geometry:
    def __init__(self):
        self.vertices = []
        self.faces = []

    @staticmethod
    def parse(data, vtx_offset, vtx_count, face_offset, face_count):
        geo = Geometry()

        # --- Vertices ---
        off = vtx_offset
        for _ in range(vtx_count):
            x, y, z = struct.unpack_from("<hhh", data, off)
            off += 6
            geo.vertices.append((
                fixed_to_float(x),
                fixed_to_float(y),
                fixed_to_float(z),
            ))

        # --- Faces (triangles) ---
        off = face_offset
        for _ in range(face_count):
            a, b, c = struct.unpack_from("<HHH", data, off)
            off += 6
            geo.faces.append((a, b, c))

        return geo