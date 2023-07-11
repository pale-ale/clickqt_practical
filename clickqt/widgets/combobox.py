from typing import Any
from PySide6.QtWidgets import QComboBox
from clickqt.widgets.basewidget import ComboBoxBase, BaseWidget
from clickqt.widgets.core.QCheckableCombobox import QCheckableComboBox
from click import Parameter, ParamType, Context, Choice

class ComboBox(ComboBoxBase):
    widget_type = QComboBox

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)
        
        if self.parent_widget is None and (default := BaseWidget.getParamDefault(param, None)) is not None:
            self.setValue(default)

    def setValue(self, value: Any):
        self.widget.setCurrentText(str(self.type.convert(str(value), self.click_command, Context(self.click_command))))

    def addItems(self, items: list[str]):
        self.widget.addItems(items)
    
    def getWidgetValue(self) -> str:
        return self.widget.currentText()
    
   
class CheckableComboBox(ComboBoxBase):
    widget_type = QCheckableComboBox

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert param.multiple, "'param.multiple' should be True"

        if self.parent_widget is None:
            self.setValue(BaseWidget.getParamDefault(param, []))

    def setValue(self, value: list[Any]):
        check_values: list[str] = []
        for v in value:
            check_values.append(str(self.type.convert(str(v), self.click_command, Context(self.click_command))))
        
        self.widget.checkItems(check_values)

    def addItems(self, items: list[str]):
        self.widget.addItems(items)

    #def isEmpty(self) -> bool:
    #    return len(self.getWidgetValue()) == 0

    def getWidgetValue(self) -> list[str]:
        return self.widget.getData()
    