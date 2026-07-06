import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal


class ScanThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)

    def __init__(self, root_path: str):
        super().__init__()
        self.root_path = root_path

    def run(self):
        results = []
        count = 0

        for root, _, files in os.walk(self.root_path):
            for filename in files:
                full_path = os.path.join(root, filename)
                try:
                    stat = os.stat(full_path)
                    ext = Path(filename).suffix.lower() or "(none)"

                    results.append({
                        'name': filename,
                        'path': full_path,
                        'size': stat.st_size,
                        'size_str': self._format_size(stat.st_size),
                        'type': ext,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                        'modified_ts': stat.st_mtime
                    })
                    count += 1

                    if count % 200 == 0:
                        self.progress.emit(count, f"Scanning... {count:,} files")

                except Exception:
                    continue

        results.sort(key=lambda x: x['modified_ts'], reverse=True)
        self.finished.emit(results)

    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"