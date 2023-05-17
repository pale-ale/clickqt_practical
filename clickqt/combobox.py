from typing import List
from PySide6.QtWidgets import QComboBox
from clickqt.base_widget import CheckBoxBase
from clickqt.QCheckableCombobox import QCheckableComboBox

class ComboBox(CheckBoxBase):
    widget_type = QComboBox

    def addItems(self, items: List[str]):
        self.widget.addItems(items)

    def getValue(self) -> str:
        return self.widget.currentText()
   
class CheckableComboBox(CheckBoxBase):
    widget_type = QCheckableComboBox

    def addItems(self, items: List[str]):
        self.widget.addItems(items)

    def getValue(self) -> List[str]:
        return self.widget.getData()