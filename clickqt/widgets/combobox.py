from typing import List
from PySide6.QtWidgets import QComboBox
from clickqt.widgets.base_widget import ComboBoxBase, BaseWidget
from clickqt.widgets.core.QCheckableCombobox import QCheckableComboBox
from clickqt.core.error import ClickQtError
from click import Context

class ComboBox(ComboBoxBase):
    widget_type = QComboBox

    def addItems(self, items: List[str]):
        self.widget.addItems(items)

    def isEmpty(self) -> bool:
        return False
    
    def getWidgetValue(self) -> str:
        return self.widget.currentText()
   
class CheckableComboBox(ComboBoxBase):
    widget_type = QCheckableComboBox

    def addItems(self, items: List[str]):
        self.widget.addItems(items)

    def getValue(self):
        if BaseWidget.isRequiredValidInput(self.param, self):
            self.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR, self.widget_name, self.param.param_type_name))

        values: list[str] = []
        
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