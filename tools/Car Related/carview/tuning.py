from PyQt6.QtWidgets import QWidget, QFormLayout, QSpinBox

# Suspected tuning offsets
TUNING_FIELDS = {
    "Mass":        (0x40, -32768, 32767),
    "Power":       (0x42, 0, 2000),
    "Top Speed":   (0x44, 0, 400),
    "Gear Ratio":  (0x48, 0, 1000),
}

class TuningEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout(self)
        self.fields = {}

    def load(self, car):
        self.car = car
        self.fields.clear()
        while self.layout.rowCount():
            self.layout.removeRow(0)

        for name, (offset, mn, mx) in TUNING_FIELDS.items():
            spin = QSpinBox()
            spin.setRange(mn, mx)
            spin.setValue(car.s16(offset))
            spin.valueChanged.connect(
                lambda v, o=offset: car.write_s16(o, v)
            )
            self.fields[name] = spin
            self.layout.addRow(name, spin)