from PySide6.QtWidgets import QCheckBox
from clickqt.widgets.base_widget import BaseWidget
from click import Parameter

class CheckBox(BaseWidget):
    widget_type = QCheckBox

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)
        self.setValue(BaseWidget.getParamDefault(param, False))
        
    def setValue(self, value: bool):
        self.widget.setChecked(value)

    def isEmpty(self) -> bool:
        return False
    
    def getWidgetValue(self) -> bool:
        return self.widget.isChecked()
    