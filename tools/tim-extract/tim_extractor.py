# tim_extractor.py
# Backend TIM extractor for PS1 games
# Can be imported by other scripts or run directly

import struct
from pathlib import Path
from PIL import Image


class TimImage:
    def __init__(self, pil_image, raw_bytes, index):
        self.image = pil_image      # Pillow Image
        self.raw_bytes = raw_bytes  # Original TIM file bytes
        self.index = index          # Order in extraction


def extract_tim_images(bin_path):
    bin_path = Path(bin_path)
    data = bin_path.read_bytes()

    tim_magic = b"\x10\x00\x00\x00"
    results = []
    offset = 0
    index = 0

    while True:
        pos = data.find(tim_magic, offset)
        if pos == -1:
            break
        if pos + 8 > len(data):
            break

        try:
            _, flags = struct.unpack("<II", data[pos:pos+8])
        except struct.error:
            break

        has_clut = bool(flags & 0x08)
        bpp_mode = flags & 0x07

        clut_block = b""
        clut_data = None
        img_block = b""

        img_block_start = pos + 8

        if has_clut:
            if img_block_start + 4 > len(data):
                offset = pos + 4
                continue
            clut_size, = struct.unpack("<I", data[img_block_start:img_block_start+4])
            if img_block_start + clut_size > len(data):
                offset = pos + 4
                continue
            clut_block = data[img_block_start:img_block_start+clut_size]
            clut_data = parse_clut(clut_block, bpp_mode)
            img_block_start += clut_size

        if img_block_start + 4 > len(data):
            offset = pos + 4
            continue
        img_size, = struct.unpack("<I", data[img_block_start:img_block_start+4])
        if img_block_start + img_size > len(data):
            offset = pos + 4
            continue
        img_block = data[img_block_start:img_block_start+img_size]

        try:
            img = parse_tim_image(img_block, clut_data, bpp_mode)
        except Exception:
            offset = pos + 4
            continue

        tim_size = (img_block_start + img_size) - pos
        tim_bytes = data[pos:pos + tim_size]

        results.append(TimImage(img, tim_bytes, index))
        index += 1
        offset = pos + tim_size

    return results



def parse_clut(clut_block, bpp_mode):
    """
    Parse CLUT into a list of (R, G, B, A) tuples.
    """
    _, x, y, w, h = struct.unpack("<HHHHH", clut_block[0:10])
    colors = []
    for i in range(w * h):
        col_val, = struct.unpack("<H", clut_block[12 + i*2:14 + i*2])
        r = (col_val & 0x1F) << 3
        g = ((col_val >> 5) & 0x1F) << 3
        b = ((col_val >> 10) & 0x1F) << 3
        a = 0 if (col_val & 0x8000) else 255
        colors.append((r, g, b, a))
    return colors


def parse_tim_image(img_block, clut, bpp_mode):
    """
    Decode TIM image into a Pillow Image.
    """
    _, x, y, w, h = struct.unpack("<HHHHH", img_block[0:10])

    if bpp_mode == 0:  # 4bpp
        img = Image.new("RGBA", (w * 4, h))
        pixels = []
        for byte in img_block[12:]:
            lo = byte & 0x0F
            hi = byte >> 4
            pixels.append(clut[lo])
            pixels.append(clut[hi])
        img.putdata(pixels)
        return img

    elif bpp_mode == 1:  # 8bpp
        img = Image.new("RGBA", (w * 2, h))
        pixels = [clut[p] for p in img_block[12:]]
        img.putdata(pixels)
        return img

    elif bpp_mode == 2:  # 16bpp direct color
        img = Image.new("RGBA", (w, h))
        pixels = []
        for i in range(0, len(img_block[12:]), 2):
            col_val, = struct.unpack("<H", img_block[12+i:14+i])
            r = (col_val & 0x1F) << 3
            g = ((col_val >> 5) & 0x1F) << 3
            b = ((col_val >> 10) & 0x1F) << 3
            a = 0 if (col_val & 0x8000) else 255
            pixels.append((r, g, b, a))
        img.putdata(pixels)
        return img

    else:
        raise ValueError(f"Unsupported BPP mode: {bpp_mode}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tim_extractor.py <file.bin>")
        sys.exit(1)

    tims = extract_tim_images(sys.argv[1])
    print(f"Found {len(tims)} TIM images.")
    for t in tims:
        out_path = Path(f"tim_{t.index}.png")
        t.image.save(out_path)
        print(f"Saved {out_path}")
