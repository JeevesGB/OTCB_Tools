from PyQt6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox

class TuningEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout(self)
        self.fields = {}

    def load(self, car):
        self.layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        # Heuristic scan: floats near sane ranges
        for offset in range(0, len(car.data), 4):
            val = car.read_float(offset)
            if 0.1 < val < 2000:
                spin = QDoubleSpinBox()
                spin.setRange(-10000, 10000)
                spin.setValue(val)
                spin.valueChanged.connect(
                    lambda v, o=offset: car.write_float(o, v)
                )
                self.layout.addRow(f"@{hex(offset)}", spin)
                self.fields[offset] = spin