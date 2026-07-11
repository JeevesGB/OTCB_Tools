"""
Shared hex-dump formatting and string-extraction helpers.

Previously this logic was duplicated in both hex_viewer.py and hex_editor.py.
Keeping it in one place means a formatting fix only needs to happen once.
"""
import re

BYTES_PER_LINE = 16


def build_hex_lines(data: bytes, start_offset: int = 0) -> list:
    """Return a list of formatted hex-dump lines (no trailing footer text)."""
    lines = []
    for i in range(0, len(data), BYTES_PER_LINE):
        chunk = data[i:i + BYTES_PER_LINE]
        hex_part = ' '.join(f'{b:02X}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        lines.append(f"{start_offset + i:08X}  {hex_part:<47}  {ascii_part}")
    return lines


def parse_hex_lines(text: str) -> bytes:
    """
    Reverse of build_hex_lines: parse an edited hex dump back into bytes.

    Each valid line looks like:
        00000010  DE AD BE EF ...  ASCII.HERE

    Lines that don't match this shape (footer/truncation notices, blank
    lines, stray text a user typed) are skipped rather than raising, so a
    user can leave notes without corrupting the save.
    """
    line_re = re.compile(r'^[0-9A-Fa-f]{8}\s{2}([0-9A-Fa-f ]+?)\s{2}')
    out = bytearray()
    for line in text.splitlines():
        m = line_re.match(line)
        if not m:
            continue
        hex_tokens = m.group(1).split()
        try:
            out.extend(int(tok, 16) for tok in hex_tokens)
        except ValueError:
            # A token wasn't valid hex (user typo) - skip this line rather
            # than silently writing garbage bytes.
            continue
    return bytes(out)


def extract_strings(data: bytes, min_length: int = 4) -> list:
    """
    Return a list of (kind, offset, string) tuples found in data.
    kind is 'ASCII' or 'UTF-16'.
    """
    results = []
    seen = set()

    for match in re.finditer(rb'[ -~]{%d,}' % min_length, data):
        offset = match.start()
        s = match.group().decode('ascii', errors='replace').strip()
        if len(s) >= min_length and s not in seen:
            seen.add(s)
            results.append(('ASCII', offset, s))

    for match in re.finditer(rb'(?:[\x20-\x7E]\x00){%d,}' % min_length, data):
        offset = match.start()
        try:
            s = match.group().decode('utf-16le', errors='replace').strip()
        except Exception:
            continue
        if len(s) >= min_length and s not in seen:
            seen.add(s)
            results.append(('UTF-16', offset, s))

    return results
