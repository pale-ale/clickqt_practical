from PySide6.QtWidgets import QLineEdit
from clickqt.base_widget import BaseWidget

class TextField(BaseWidget):
    widget_type = QLineEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.setValue(options.get("default")() if callable(options.get("default")) \
                else options.get("default") or "")
        
        if kwargs.get("o") is not None and hasattr(kwargs["o"], "hide_input") and kwargs["o"].hide_input:
            self.widget.setEchoMode(QLineEdit.EchoMode.Password)

    def setValue(self, value: str):
        self.widget.setText(value)

    def getValue(self) -> str:
        return self.widget.text()
   