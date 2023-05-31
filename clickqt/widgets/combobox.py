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
        return self.widget.currentText(), ClickQtError()
   
class CheckableComboBox(ComboBoxBase):
    widget_type = QCheckableComboBox

    def addItems(self, items: List[str]):
        self.widget.addItems(items)

    def getValue(self) -> Tuple[List[str], ClickQtError]:
        return self.widget.getData(), ClickQtError()