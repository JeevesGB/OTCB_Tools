# File Scanner & Hex Viewer

A powerful Python + PyQt6 desktop application for scanning, browsing, and analyzing files with hex viewing and string extraction capabilities.

## Features

- **Directory Tree Navigation** – Browse folders with a rooted file tree
- **File Table View** – Shows Name, Type, Size, Modified Date, and Full Path
- **Filter & Sort** – Filter the file table by name, extension, or path, and click any column header to sort
- **Hex Preview** – View first 100MB of any file in classic hex + ASCII format, loaded on a background thread so the UI never freezes
- **String Extraction** – Automatically finds ASCII and UTF-16 strings
- **Hex Editor** – Separate window for editing files up to 20MB, with automatic `.bak` backups before saving
- **Full Recursive Scan** – Scan entire directory trees, with a progress bar and a Cancel button

## Requirements

- Python 3.9+
- PyQt6

## Installation

### Option 1: Run from source

1. Clone or download the project
2. Install dependencies:

```
pip install -r requirements.txt
```

### Option 2: Install as a package

```
pip install .
```

This installs an `otcb-fileview` command you can run from anywhere.

## Running

**From source:**
1. Open CMD inside the *src* folder.
2. Type `python main.py`

**If installed as a package:**
```
otcb-fileview
```

## Notes

- The Hex Viewer truncates files over 100MB to the first 100MB.
- The Hex Editor caps out at 20MB, since edits are held in memory and the whole file is rewritten on save. Use the Hex Viewer to inspect larger files.
- Saving in the Hex Editor always writes a `.bak` copy of the original file alongside it first.

## License

MIT — see [LICENSE](../../LICENSE).

###### JejCo 2026
