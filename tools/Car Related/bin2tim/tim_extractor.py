import struct
import os
import numpy as np
from PIL import Image

# ==============================
# Helpers
# ==============================

def bgr555_to_rgb(c):
    r = ((c >> 10) & 0x1F) << 3
    g = ((c >> 5) & 0x1F) << 3
    b = (c & 0x1F) << 3
    return (r, g, b)

def find_tim_offsets(data):
    offsets = []
    for i in range(0, len(data) - 4, 4):
        if data[i:i+4] == b'\x10\x00\x00\x00':
            offsets.append(i)
    return offsets

# ==============================
# TIM structure
# ==============================

class TIM:
    def __init__(self, offset):
        self.offset = offset
        self.end = None
        self.bpp = None
        self.has_clut = False
        self.clut = None
        self.image = None
        self.raw = None

# ==============================
# TIM Parser
# ==============================

def parse_tim(data, offset):
    pos = offset

    magic, flags = struct.unpack_from('<II', data, pos)
    pos += 8
    if magic != 0x10:
        raise ValueError("Invalid TIM")

    tim = TIM(offset)

    bpp_flag = flags & 0x07
    tim.bpp = {0: 4, 1: 8, 2: 16}.get(bpp_flag)
    tim.has_clut = bool(flags & 0x08)

    # ---- CLUT ----
    if tim.has_clut:
        clut_size = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        x, y, w, h = struct.unpack_from('<HHHH', data, pos)
        pos += 8

        clut_data = data[pos:pos + clut_size - 12]
        pos += clut_size - 12

        tim.clut = {
            "w": w,
            "h": h,
            "data": clut_data
        }

    # ---- IMAGE ----
    img_size = struct.unpack_from('<I', data, pos)[0]
    pos += 4
    x, y, w_words, h = struct.unpack_from('<HHHH', data, pos)
    pos += 8

    pixel_data = data[pos:pos + img_size - 12]
    pos += img_size - 12

    tim.image = {
        "w_words": w_words,
        "h": h,
        "data": pixel_data
    }

    tim.end = pos
    tim.raw = data[offset:pos]
    return tim

# ==============================
# Decode TIM → PNG
# ==============================

def decode_clut(clut_bytes):
    colors = []
    for i in range(0, len(clut_bytes), 2):
        c = struct.unpack_from('<H', clut_bytes, i)[0]
        colors.append(bgr555_to_rgb(c))
    return colors

def tim_to_image(tim):
    w_pixels = tim.image["w_words"] * (16 // tim.bpp)
    h = tim.image["h"]
    data = tim.image["data"]

    if tim.bpp == 4:
        indices = np.zeros(w_pixels * h, dtype=np.uint8)
        for i, b in enumerate(data):
            indices[i * 2] = b & 0x0F
            indices[i * 2 + 1] = b >> 4
        clut = decode_clut(tim.clut["data"])
        img = Image.new("RGB", (w_pixels, h))
        img.putdata([clut[i] for i in indices])

    elif tim.bpp == 8:
        indices = np.frombuffer(data, dtype=np.uint8)
        clut = decode_clut(tim.clut["data"])
        img = Image.new("RGB", (w_pixels, h))
        img.putdata([clut[i] for i in indices])

    elif tim.bpp == 16:
        img = Image.new("RGB", (w_pixels, h))
        pixels = []
        for i in range(0, len(data), 2):
            c = struct.unpack_from('<H', data, i)[0]
            pixels.append(bgr555_to_rgb(c))
        img.putdata(pixels)

    return img

# ==============================
# Extract ALL TIMs from BIN
# ==============================

def extract_bin(bin_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    with open(bin_path, "rb") as f:
        data = f.read()

    offsets = find_tim_offsets(data)
    print(f"Found {len(offsets)} TIM(s)")

    for i, off in enumerate(offsets):
        tim = parse_tim(data, off)
        img = tim_to_image(tim)

        name = f"tim_{i:03d}_bpp{tim.bpp}_{img.width}x{img.height}.png"
        img.save(os.path.join(out_dir, name))
        print(f"Extracted {name}")

# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    BIN_FILE = r"C:\Users\there\Desktop\DEV\Github\OTCB_Tools\tools\Car Related\bin2tim\CAR.BIN"
    OUT_DIR = "extracted_tim"

    extract_bin(BIN_FILE, OUT_DIR)