from PyQt6.QtWidgets import QCheckBox
from clickqt.base_widget import BaseWidget

class CheckBox(BaseWidget):
    widget_type = QCheckBox

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.setValue(options.get("default")() if callable(options.get("default")) \
                else options.get("default") or False)

    def setValue(self, value: bool):
        self.widget.setChecked(value)

    def getValue(self) -> bool:
        return self.widget.isChecked()
    