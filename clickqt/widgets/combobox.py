from typing import List
from PySide6.QtWidgets import QComboBox
from clickqt.widgets.base_widget import ComboBoxBase
from clickqt.widgets.core.QCheckableCombobox import QCheckableComboBox
from clickqt.core.error import ClickQtError
from click import Context

class ComboBox(ComboBoxBase):
    widget_type = QComboBox

    def addItems(self, items: List[str]):
        self.widget.addItems(items)
    
    def getWidgetValue(self) -> str:
        return self.widget.currentText()
    
    def getWidgetValueToString(self) -> str:
        return str(self.getWidgetValue())
   
class CheckableComboBox(ComboBoxBase):
    widget_type = QCheckableComboBox

    def addItems(self, items: List[str]):
        self.widget.addItems(items)

    def getValue(self):
        values = []

        for v in self.getWidgetValue():
            try: # Try to convert the provided value into the corresponding click object type 
                values.append(self.param.type.convert(value=v, param=self.param, ctx=Context(self.click_command)))
            except Exception as e:
                return (None, ClickQtError(ClickQtError.ErrorType.CONVERSION_ERROR, self.widget_name, e))
      
        try: # Try to convert the provided value the corresponding click object type 
            return (self.param.process_value(Context(self.click_command), values), ClickQtError())
        except Exception as e:
            return (None, ClickQtError(ClickQtError.ErrorType.CALLBACK_VALIDATION_ERROR, self.widget_name, e))


    def getWidgetValue(self) -> List[str]:
        return self.widget.getData()
    
    def getWidgetValueToString(self) -> str:
        return " ".join(self.getWidgetValue())