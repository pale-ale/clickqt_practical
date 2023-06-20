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

    def isEmpty(self) -> bool:
        return len(self.getWidgetValue()) == 0

    def getWidgetValue(self) -> List[str]:
        return self.widget.getData()
    