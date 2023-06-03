from typing import List, Tuple
from PySide6.QtWidgets import QComboBox
from clickqt.widgets.base_widget import ComboBoxBase
from clickqt.widgets.core.QCheckableCombobox import QCheckableComboBox
from clickqt.core.error import ClickQtError

class ComboBox(ComboBoxBase):
    widget_type = QComboBox

    def addItems(self, items: List[str]):
        self.widget.addItems(items)

    def getValue(self) -> Tuple[str, ClickQtError]:
        value, err = self.callback_validate()
        if err.type != ClickQtError.ErrorType.NO_ERROR:
            self.handleValid(False)
            return (value, err)
        
        return (self.getWidgetValue(), ClickQtError())
    
    def getWidgetValue(self) -> str:
        return self.widget.currentText()
   
class CheckableComboBox(ComboBoxBase):
    widget_type = QCheckableComboBox

    def addItems(self, items: List[str]):
        self.widget.addItems(items)

    def getValue(self) -> Tuple[List[str], ClickQtError]:
        value, err = self.callback_validate()
        if err.type != ClickQtError.ErrorType.NO_ERROR:
            self.handleValid(False)
            return (value, err)
        
        return (self.getWidgetValue(), ClickQtError())
    
    def getWidgetValue(self) -> List[str]:
        return self.widget.getData()