# str_converter.py

import os
import struct
import io
from PIL import Image

def convert_str_to_avi(path, log_callback):
    log_callback(f"[STR→AVI] Processing file: {path}")

    try:
        with open(path, 'rb') as f:
            header = f.read(16)
            log_callback(f"[STR→AVI] Header: {header.hex()}")
            output_path = os.path.splitext(path)[0] + ".avi"
            with open(output_path, 'wb') as out:
                out.write(b'RIFF....AVI')
                out.write(f.read())
            log_callback(f"[STR→AVI] Output saved to: {output_path}")
    except Exception as e:
        log_callback(f"[STR→AVI] Error: {e}")

def convert_avi_to_str(path, log_callback):
    log_callback(f"[AVI→STR] Processing file: {path}")

    try:
        with open(path, 'rb') as f:
            header = f.read(12)
            log_callback(f"[AVI→STR] Header: {header.hex()}")
            output_path = os.path.splitext(path)[0] + ".str"
            with open(output_path, 'wb') as out:
                out.write(b'STRHEAD')
                out.write(f.read())
            log_callback(f"[AVI→STR] Output saved to: {output_path}")
    except Exception as e:
        log_callback(f"[AVI→STR] Error: {e}")

def extract_str_frames(path, log_callback):
    frames = []
    try:
        with open(path, 'rb') as f:
            sector_size = 2048
            jpeg_data = bytearray()
            while True:
                sector = f.read(sector_size)
                if len(sector) < sector_size:
                    break

                # Skip 24-byte header; start at byte 24
                data = sector[24:]
                jpeg_data.extend(data)

                # Check for start of JPEG (0xFFD8)
                while True:
                    start = jpeg_data.find(b'\xff\xd8')
                    end = jpeg_data.find(b'\xff\xd9', start)
                    if start != -1 and end != -1:
                        jpeg = jpeg_data[start:end+2]
                        try:
                            img = Image.open(io.BytesIO(jpeg)).convert("RGB")
                            frames.append(img)
                        except Exception as e:
                            log_callback(f"[Decode] JPEG error: {e}")
                        jpeg_data = jpeg_data[end+2:]
                    else:
                        break

        log_callback(f"[STR] Extracted {len(frames)} frame(s)")
    except Exception as e:
        log_callback(f"[STR] Error reading file: {e}")
    return frames
