import struct

class CarFile:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            self.data = bytearray(f.read())

    def u8(self, o):  return self.data[o]
    def s16(self, o): return struct.unpack_from("<h", self.data, o)[0]
    def u16(self, o): return struct.unpack_from("<H", self.data, o)[0]
    def s32(self, o): return struct.unpack_from("<i", self.data, o)[0]
    def u32(self, o): return struct.unpack_from("<I", self.data, o)[0]

    def write_s16(self, o, v):
        struct.pack_into("<h", self.data, o, v)

    def write_u32(self, o, v):
        struct.pack_into("<I", self.data, o, v)

    def save(self, out_path=None):
        with open(out_path or self.path, "wb") as f:
            f.write(self.data)