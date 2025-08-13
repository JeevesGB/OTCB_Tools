# TIX TIM Explorer

A Windows desktop GUI tool for **extracting, viewing, and repacking** `.TIM` textures from PlayStation 1 `.TIX` texture archives.  
Built in Python using PyQt5.  

---

##   Features
- **Open `.TIX` files** and automatically detect contained `.TIM` images.
- **View TIM textures** in a scrollable preview list.
- **Extract all TIMs** to a chosen folder.
- **Extract individual TIMs** by selecting them.
- **Repack `.TIX` files** from a folder of `.TIM` images (preserves order).
- **Error handling** for corrupt or unsupported TIM entries.

---

##  Requirements

- Python **3.10+**  
- Install dependencies:
```bash
pip install PyQt5 Pillow
```

---

##  Usage

1. **Run the tool**  
   ```bash
   python tix-2-tim.py
   ```
2. **Open a `.TIX` file**  
   - Use the **File → Open** menu or the toolbar button.
3. **View TIM previews**  
   - Click an entry in the list to see it in the preview panel.
4. **Extract TIMs**  
   - `File → Extract All` to dump all TIMs into a folder.
   - Right-click → Extract Selected for one texture.
5. **Repack**  
   - `File → Repack` → choose folder of `.TIM` files → choose save location.

---

##  TIM Format Support

This tool supports:
- 4-bit and 8-bit indexed TIMs
- 16-bit direct color TIMs  
- Automatic CLUT (palette) detection  
- Skips invalid or corrupted entries to avoid crashes  

---

##  Known Limitations
- No editing of TIMs in-app — must be done in external TIM editor.
- Doesn’t yet support 24-bit TIMs (most `.TIX` don’t use these).
- Repacking assumes same TIM dimensions/order as original archive.

---

##  Building to EXE
To make a standalone Windows build:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=icon.ico tix-2-tim.py
```
The `.exe` will be in the `dist` folder.

---
