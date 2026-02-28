import struct

class BinaryFile:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            self.data = f.read()

    def u8(self, o):  return self.data[o]
    def s16(self, o): return struct.unpack_from("<h", self.data, o)[0]
    def u16(self, o): return struct.unpack_from("<H", self.data, o)[0]
    def u32(self, o): return struct.unpack_from("<I", self.data, o)[0]

    def slice(self, o, size):
        return self.data[o:o+size]