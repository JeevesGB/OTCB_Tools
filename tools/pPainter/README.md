# pPainter

pPainter is a lightweight painting/drawing application built with Python and PyQt6.  
It allows users to create and edit images with a simple and intuitive interface supporting basic brush tools, layers, color selection, and file export.

---

## Features

- Brush and eraser tools with adjustable size  
- Color picker and palette support  
- Multiple layers with basic layer controls (add, delete, reorder)  
- Undo/redo functionality  
- Export drawings as PNG files  
- Simple UI optimized for quick sketches and edits

---

## Requirements

- Python 3.9 or newer  
- PyQt6  
- (Linux) Required system packages for Qt xcb plugin (see below)  
- (Windows) Python 3.x with PyQt6

---

## Installation and Build Instructions

### Linux

1. **Install dependencies**

```bash
sudo apt update
sudo apt install python3 python3-pip libxcb-xinerama0 libxcb-cursor0
pip3 install pyqt6
```

2. **Run the application**

```bash
python3 main.py
```

> **Note:** If you encounter Wayland errors, try launching with the Qt platform set to `xcb`:

```bash
QT_QPA_PLATFORM=xcb python3 main.py
```

---

### Windows

1. Install Python 3.x for Windows from https://python.org  
2. Open Command Prompt and install PyQt6:

```cmd
pip install pyqt6
```

3. Run the application:

```cmd
python main.py
```

---

## Building Windows EXE

### Method 1: On Windows (Recommended)

1. Install Python and dependencies:
```cmd
pip install pyqt6 pillow pyinstaller
```

2. Build the executable:
```cmd
pyinstaller --onefile --windowed --name pPainter main.py
```

3. Your `.exe` will be in the `dist/` folder

### Method 2: On Linux with Virtual Environment

If you get an "externally-managed-environment" error on Linux:

```bash
# Install system dependencies (if needed)
sudo apt install python3-full python3-venv

# Create virtual environment
python3 -m venv painter_builder

# Activate it
source painter_builder/bin/activate

# Install dependencies
pip install pyinstaller pyqt6 pillow

# Build executable
pyinstaller --onefile --windowed --name pPainter main.py

# Deactivate when done
deactivate
```

### Method 3: Using pipx (Alternative for Linux)

```bash
# Install pipx
sudo apt install pipx

# Create temporary environment and build
python3 -m venv temp_build
source temp_build/bin/activate
pip install pyinstaller pyqt6 pillow
pyinstaller --onefile --windowed --name pPainter main.py
deactivate
```

### Method 4: Cross-compiling Windows `.exe` on Linux (Using Wine)

If you want to build a Windows executable (`.exe`) from your Linux machine, follow these steps:

1. Install Wine:

```bash
sudo apt update
sudo apt install wine64 wine32
```

2. Download and install Windows Python inside Wine:

```bash
wine python-3.x.x.exe
```

3. Install PyInstaller and PyQt6 in Wine Python:

```bash
wine "C:\\path\\to\\python.exe" -m pip install pyinstaller pyqt6 pillow
```

4. Run PyInstaller inside Wine to build your `.exe`:

```bash
wine "C:\\path\\to\\python.exe" -m PyInstaller --onefile --windowed main.py
```

5. Your Windows executable will be in the `dist` folder inside the Wine environment.

---

## PyInstaller Options Explained

- `--onefile`: Creates a single executable file instead of a folder with dependencies
- `--windowed`: Prevents console window from appearing (GUI apps only)
- `--name pPainter`: Sets the executable name to "pPainter.exe"

---

## Troubleshooting

- **"externally-managed-environment" error**: Use a virtual environment (Method 2 above)

- **Wayland errors on Linux**: Qt apps sometimes have issues with Wayland compositors. Use the `QT_QPA_PLATFORM=xcb` environment variable to force X11 backend.

- **Missing Qt plugins (xcb)**: Install system packages like `libxcb-xinerama0` and `libxcb-cursor0` to resolve Qt plugin loading errors.

- **Wine PyInstaller build fails**: Make sure Wine is fully installed and that you installed Windows Python and PyInstaller inside the Wine prefix correctly.

- **EXE is too large**: PyInstaller includes the entire Python runtime. This is normal - expect 50-100MB+ file sizes.

---

## License

MIT License

---

## Author

_jej_