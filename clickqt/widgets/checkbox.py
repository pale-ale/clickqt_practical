from PySide6.QtWidgets import QCheckBox
from clickqt.widgets.basewidget import BaseWidget
from click import Parameter, Context, ParamType, BOOL
from typing import Any

class CheckBox(BaseWidget):
    widget_type = QCheckBox

    def __init__(self, otype:ParamType, param:Parameter, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        assert isinstance(otype, type(BOOL)), f"'otype' must be of type '{type(BOOL)}', but is '{type(otype)}'."

        if self.parent_widget is None:
            self.setValue(BaseWidget.getParamDefault(param, False))
        
    def setValue(self, value:Any):
        self.widget.setChecked(bool(self.type.convert(str(value), self.click_command, Context(self.click_command))))
    
    def getWidgetValue(self) -> bool:
        return self.widget.isChecked()
    