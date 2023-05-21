from typing import List
from PySide6.QtWidgets import QComboBox
from clickqt.widgets.base_widget import ComboBoxBase
from clickqt.widgets.core.QCheckableCombobox import QCheckableComboBox

class ComboBox(ComboBoxBase):
    widget_type = QComboBox

    def addItems(self, items: List[str]):
        self.widget.addItems(items)

    def getValue(self) -> str:
        return self.widget.currentText()
   
class CheckableComboBox(ComboBoxBase):
    widget_type = QCheckableComboBox

    def addItems(self, items: List[str]):
        self.widget.addItems(items)

    def getValue(self) -> List[str]:
        return self.widget.getData()