from PyQt6.QtCore import QAbstractTableModel, Qt


class FileTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self.files = data or []
        self.headers = ["Name", "Type", "Size", "Modified", "Full Path"]

    def rowCount(self, parent=None):
        return len(self.files)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            row = self.files[index.row()]
            col = index.column()
            if col == 0: return row['name']
            if col == 1: return row['type']
            if col == 2: return row['size_str']
            if col == 3: return row['modified']
            if col == 4: return row['path']
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

    def get_file_info(self, row: int):
        return self.files[row] if 0 <= row < len(self.files) else None