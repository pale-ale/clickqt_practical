from PySide6.QtWidgets import QLineEdit
from clickqt.widgets.base_widget import BaseWidget
from click import Parameter

class TextField(BaseWidget):
    widget_type = QLineEdit

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)
        self.setValue(BaseWidget.getParamDefault(param, ""))

    def setValue(self, value: str):
        self.widget.setText(value)
    
    def getWidgetValue(self) -> str:
        return self.widget.text()
   