import struct
import os
import numpy as np
from PIL import Image

# ==============================
# Helpers
# ==============================

def bgr555_to_rgb(c):
    r5 = (c >> 0) & 0x1F
    g5 = (c >> 5) & 0x1F
    b5 = (c >> 10) & 0x1F

    # expand 5-bit to 8-bit properly
    r = (r5 << 3) | (r5 >> 2)
    g = (g5 << 3) | (g5 >> 2)
    b = (b5 << 3) | (b5 >> 2)

    return (r, g, b)

def rgb_to_bgr555(r, g, b):
    return ((r >> 3) << 10) | ((g >> 3) << 5) | (b >> 3)

def find_tim_offsets(data):
    return [
        i for i in range(0, len(data) - 4, 4)
        if data[i:i+4] == b"\x10\x00\x00\x00"
    ]

# ==============================
# TIM Structure
# ==============================

class TIM:
    def __init__(self, offset):
        self.offset = offset
        self.end = None
        self.bpp = None
        self.has_clut = False
        self.clut = None
        self.image = None

# ==============================
# Parse TIM
# ==============================

def parse_tim(data, offset):
    pos = offset
    magic, flags = struct.unpack_from("<II", data, pos)
    pos += 8

    if magic != 0x10:
        raise ValueError("Not a TIM")

    tim = TIM(offset)

    bpp_flag = flags & 0x07
    tim.bpp = {0:4, 1:8, 2:16}[bpp_flag]
    tim.has_clut = bool(flags & 0x08)

    if tim.has_clut:
        clut_size = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        x, y, w, h = struct.unpack_from("<HHHH", data, pos)
        pos += 8
        clut_data = data[pos:pos + clut_size - 12]
        pos += clut_size - 12
        tim.clut = {"w": w, "h": h, "data": clut_data}

    img_size = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    x, y, w_words, h = struct.unpack_from("<HHHH", data, pos)
    pos += 8
    pixel_data = data[pos:pos + img_size - 12]
    pos += img_size - 12

    tim.image = {
        "w_words": w_words,
        "h": h,
        "data": pixel_data
    }

    tim.end = pos
    return tim

# ==============================
# Decode TIM → PIL Image
# ==============================

def decode_clut(clut_bytes):
    return [
        bgr555_to_rgb(struct.unpack_from("<H", clut_bytes, i)[0])
        for i in range(0, len(clut_bytes), 2)
    ]

def tim_to_image(tim):
    w = tim.image["w_words"] * (16 // tim.bpp)
    h = tim.image["h"]
    data = tim.image["data"]

    if tim.bpp in (4, 8):
        clut = decode_clut(tim.clut["data"])

    if tim.bpp == 4:
        indices = []
        for b in data:
            indices.append(b & 0x0F)
            indices.append(b >> 4)
        pixels = [clut[i] for i in indices[:w*h]]

    elif tim.bpp == 8:
        pixels = [clut[b] for b in data[:w*h]]

    else:
        pixels = [
            bgr555_to_rgb(struct.unpack_from("<H", data, i)[0])
            for i in range(0, len(data), 2)
        ]

    img = Image.new("RGB", (w, h))
    img.putdata(pixels)
    return img

# ==============================
# BIN → PNG Extraction
# ==============================

def extract_bin(bin_path, out_root):
    bin_name = os.path.splitext(os.path.basename(bin_path))[0]
    out_dir = os.path.join(out_root, bin_name)
    os.makedirs(out_dir, exist_ok=True)

    with open(bin_path, "rb") as f:
        data = f.read()

    offsets = find_tim_offsets(data)

    for i, off in enumerate(offsets):
        tim = parse_tim(data, off)
        img = tim_to_image(tim)

        w = img.width
        h = img.height

        base = f"tim_{i:03d}_bpp{tim.bpp}_{w}x{h}"

        # ---- save PNG ----
        img.save(os.path.join(out_dir, base + ".png"))

        # ---- save raw TIM ----
        with open(os.path.join(out_dir, base + ".tim"), "wb") as f:
            f.write(data[off:tim.end])

# ==============================
# PNG → TIM Rebuild (SAFE)
# ==============================

def image_to_indices(img, clut):
    clut_map = {rgb: i for i, rgb in enumerate(clut)}
    indices = []

    for p in img.getdata():
        if p not in clut_map:
            raise ValueError("Image uses colors not in original CLUT")
        indices.append(clut_map[p])

    return indices

def rebuild_tim_pixels(tim, img):
    w = tim.image["w_words"] * (16 // tim.bpp)
    h = tim.image["h"]

    if img.size != (w, h):
        raise ValueError("Image size mismatch")

    if tim.bpp in (4, 8):
        clut = decode_clut(tim.clut["data"])
        indices = image_to_indices(img, clut)

        if tim.bpp == 4:
            out = bytearray()
            for i in range(0, len(indices), 2):
                out.append(indices[i] | (indices[i+1] << 4))
        else:
            out = bytearray(indices)

    else:
        out = bytearray()
        for r, g, b in img.getdata():
            out += struct.pack("<H", rgb_to_bgr555(r, g, b))

    if len(out) != len(tim.image["data"]):
        raise ValueError("Pixel data size mismatch")

    return out

def rebuild_bin(original_bin, png_dir, out_bin):
    with open(original_bin, "rb") as f:
        data = bytearray(f.read())

    offsets = find_tim_offsets(data)

    for i, off in enumerate(offsets):
        tim = parse_tim(data, off)

        w = tim.image["w_words"] * (16 // tim.bpp)
        h = tim.image["h"]
        png = f"tim_{i:03d}_bpp{tim.bpp}_{w}x{h}.png"
        path = os.path.join(png_dir, png)

        if not os.path.exists(path):
            continue

        img = Image.open(path).convert("RGB")
        new_pixels = rebuild_tim_pixels(tim, img)

        pixel_offset = tim.end - len(tim.image["data"])
        data[pixel_offset:pixel_offset + len(new_pixels)] = new_pixels

    with open(out_bin, "wb") as f:
        f.write(data)