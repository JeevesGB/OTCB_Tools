def repack(original_bytes, edits):
    data = bytearray(original_bytes)

    for offset, new_bytes in edits.items():
        data[offset:offset+len(new_bytes)] = new_bytes

    return bytes(data)