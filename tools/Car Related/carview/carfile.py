import struct

class CarFile:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            self.data = bytearray(f.read())

    def read_float(self, off):
        return struct.unpack_from("<f", self.data, off)[0]

    def write_float(self, off, val):
        struct.pack_into("<f", self.data, off, val)

    def save(self, path=None):
        with open(path or self.path, "wb") as f:
            f.write(self.data)