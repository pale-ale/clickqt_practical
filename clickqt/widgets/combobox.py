from typing import List
from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Qt
from clickqt.widgets.base_widget import ComboBoxBase, BaseWidget
from clickqt.widgets.core.QCheckableCombobox import QCheckableComboBox
from clickqt.core.error import ClickQtError
from click import Context, Parameter

class ComboBox(ComboBoxBase):
    widget_type = QComboBox

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)
        self.setValue(BaseWidget.getParamDefault(param, None)) # Ignore, if there is no default

    def setValue(self, value: str):
        if isinstance(value, str):
            if (index := self.widget.findText(value, Qt.MatchFlag.MatchCaseSensitive if self.param.type.case_sensitive 
                                              else Qt.MatchFlag.MatchFixedString)) >= 0:
                self.widget.setCurrentIndex(index)

    def addItems(self, items: List[str]):
        self.widget.addItems(items)
    
    def getWidgetValue(self) -> str:
        return self.widget.currentText()
   
class CheckableComboBox(ComboBoxBase):
    widget_type = QCheckableComboBox

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)
        self.setValue(BaseWidget.getParamDefault(param, []))

    def setValue(self, value: list[str]):
        if isinstance(value, list):
            self.widget.checkItems(value, self.param.type.case_sensitive)

    def addItems(self, items: List[str]):
        self.widget.addItems(items)

    def getValue(self):
        value_missing = False
        if self.isEmpty():
            default = BaseWidget.getParamDefault(self.param, None)
            if self.param.required and default is None:
                self.handleValid(False)
                return (None, ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR, self.widget_name, self.param.param_type_name))
            elif default is not None: # Overwrite the empty widget with the default value and execute with this (new) value
                self.setValue(default)
            else: # param is not required and there is no default -> value is None
                value_missing = True # But callback should be considered

        values: list[str]|None = None

        if not value_missing:
            values = []
            for v in self.getWidgetValue():
                try: # Try to convert the provided value into the corresponding click object type 
                    values.append(self.param.type.convert(value=v, param=self.param, ctx=Context(self.click_command)))
                except Exception as e:
                    return (None, ClickQtError(ClickQtError.ErrorType.CONVERTING_ERROR, self.widget_name, e))

        try: # Consider callbacks
            return (self.param.process_value(Context(self.click_command), values), ClickQtError())
        except Exception as e:
            return (None, ClickQtError(ClickQtError.ErrorType.PROCESSING_VALUE_ERROR, self.widget_name, e))

    def isEmpty(self) -> bool:
        return len(self.getWidgetValue()) == 0

    def getWidgetValue(self) -> List[str]:
        return self.widget.getData()