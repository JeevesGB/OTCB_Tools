import struct
import os
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

    bpp_flag = flags & 0x07  # Extract bpp flag from flags byte
    try:
        tim.bpp = {0:4, 1:8, 2:16}[bpp_flag]  # Map bpp_flag to bpp
    except KeyError:
        print(f"Warning: Unexpected bpp flag {bpp_flag} at offset {offset}. Skipping this TIM image.")
        return None  # Skip images with an unexpected bpp_flag

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
    w = tim.image["w_words"] * (16 // tim.bpp)  # width in pixels
    h = tim.image["h"]  # height in pixels
    data = tim.image["data"]  # raw pixel data

    print(f"Decoding image: {w}x{h}, bpp={tim.bpp}")

    # Skip images with invalid dimensions
    if w == 0 or h == 0:
        print(f"Warning: TIM at offset {tim.offset} has invalid dimensions (0x0). Skipping this image.")
        return None  # Skip images with invalid dimensions

    # Ensure the pixel count matches
    expected_pixel_count = w * h
    actual_pixel_count = len(data)  # Actual data length in bytes (should be equal to expected pixel count for bpp=8)
    print(f"Expected pixel count: {expected_pixel_count}, actual data length: {actual_pixel_count}")

    if expected_pixel_count != actual_pixel_count:
        if actual_pixel_count == 0:
            print(f"Warning: TIM at offset {tim.offset} has no pixel data. Skipping this image.")
            return None  # Skip empty or corrupt images
        elif actual_pixel_count < expected_pixel_count:
            print(f"Warning: Expected {expected_pixel_count} pixels, but got {actual_pixel_count} bytes of data. Skipping this image.")
            return None  # Skip images with incomplete data
        print(f"Warning: Expected {expected_pixel_count} pixels, but got {actual_pixel_count} bytes of data.")
        raise ValueError(f"Mismatch in pixel count: expected {expected_pixel_count}, got {actual_pixel_count}")

    # Check if the TIM has a CLUT and decode it if it exists (only for bpp=4 or 8)
    if tim.bpp in (4, 8):
        if tim.clut is not None:
            clut = decode_clut(tim.clut["data"])
        else:
            print(f"Warning: TIM at offset {tim.offset} has no CLUT. Skipping.")
            return None  # Return None if CLUT is missing

    # Handle the BPP cases
    pixels = []
    if tim.bpp == 4:
        # Extract 4bpp pixel indices from the data
        indices = []
        for b in data:
            indices.append(b & 0x0F)
            indices.append(b >> 4)
        pixels = [clut[i] for i in indices[:expected_pixel_count]]

    elif tim.bpp == 8:
        # Extract 8bpp pixel indices from the data (1 byte per pixel)
        pixels = [clut[b] for b in data[:expected_pixel_count]]

    else:
        # For 16bpp, the pixel data is stored directly as RGB565, not using a CLUT
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
        if tim is None:
            continue  # Skip invalid TIM objects

        img = tim_to_image(tim)

        if img is None:
            continue  # Skip if the image decoding failed

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