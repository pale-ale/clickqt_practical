from PySide6.QtWidgets import QLineEdit
from clickqt.widgets.base_widget import BaseWidget
from click import Parameter

class TextField(BaseWidget):
    widget_type = QLineEdit

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)
        default = BaseWidget.getParamDefault(param, "")
        if isinstance(default, str):
            self.setValue(default)

    def setValue(self, value: str):
        self.widget.setText(value)

    def isEmpty(self) -> bool:
        return self.getWidgetValue() == ""
    
    def getWidgetValue(self) -> str:
        return self.widget.text()
   