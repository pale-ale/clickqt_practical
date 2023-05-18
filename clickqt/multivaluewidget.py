from PySide6.QtWidgets import QGroupBox, QHBoxLayout
from clickqt.base_widget import BaseWidget
from click import Parameter
from typing import Callable, Any

class MultiValueWidget(BaseWidget):
    widget_type = QGroupBox()
    
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        
    def setValue(self, value):
        return super().setValue(value)
    
    def getValue(self):
        return super().getValue()