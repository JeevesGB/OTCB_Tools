import os
import struct

TIM_MAGIC = b'\x10\x00\x00\x00'
VALID_MODES = {0, 1, 2, 3}


def read_u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def parse_tim(data, offset):
    try:
        if data[offset:offset+4] != TIM_MAGIC:
            return None

        flags = read_u32(data, offset + 4)
        mode = flags & 0x7
        has_clut = (flags & 0x8) != 0

        if mode not in VALID_MODES:
            return None

        pos = offset + 8

        if has_clut:
            clut_size = read_u32(data, pos)

            if clut_size < 12 or clut_size > 0x10000:
                return None

            pos += clut_size

        img_size = read_u32(data, pos)

        if img_size < 12 or img_size > 0x800000:
            return None

        pos += img_size

        if pos > len(data):
            return None

        return pos

    except:
        return None


def scan_tim(car_file, script_dir):

    with open(car_file, "rb") as f:
        data = f.read()

    base = os.path.splitext(os.path.basename(car_file))[0]
    outdir = os.path.join(script_dir, base)

    os.makedirs(outdir, exist_ok=True)

    offset = 0
    found = 0

    print(f"\nScanning {base}.CAR")

    while offset < len(data) - 8:

        if data[offset:offset+4] == TIM_MAGIC:

            end = parse_tim(data, offset)

            if end:
                size = end - offset

                name = f"tim_{offset:08X}.tim"
                outpath = os.path.join(outdir, name)

                with open(outpath, "wb") as f:
                    f.write(data[offset:end])

                print(f"  TIM found at {hex(offset)} size {hex(size)}")

                found += 1
                offset = end
                continue

        offset += 1

    print(f"  Total TIMs extracted: {found}")


def main():

    script_dir = os.path.dirname(os.path.abspath(__file__))

    car_files = [
        f for f in os.listdir(script_dir)
        if f.lower().endswith(".car")
    ]

    if not car_files:
        print("No .CAR files found.")
        return

    print(f"Found {len(car_files)} CAR files.\n")

    for car in car_files:

        car_path = os.path.join(script_dir, car)

        scan_tim(car_path, script_dir)

    print("\nAll files processed.")


if __name__ == "__main__":
    main()