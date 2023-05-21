from PySide6.QtWidgets import QLineEdit
from clickqt.widgets.base_widget import BaseWidget
from typing import Tuple
from clickqt.core.error import ClickQtError

class TextField(BaseWidget):
    widget_type = QLineEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.setValue(options.get("default")() if callable(options.get("default")) \
                else options.get("default") or "")

    def setValue(self, value: str):
        self.widget.setText(value)

    def getValue(self) -> Tuple[str, ClickQtError]:
        return self.widget.text(), ClickQtError.NO_ERROR
   