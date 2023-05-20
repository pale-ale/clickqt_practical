from PySide6.QtWidgets import QGroupBox, QHBoxLayout
from clickqt.base_widget import BaseWidget
from click import Parameter
from typing import Callable, Any

class MultiValueWidget(BaseWidget):
    widget_type = QGroupBox()
    
    def __init__(self, options, otype, onargs, *args, widgetsource:Callable[[Any], BaseWidget]=None, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.children = []
        self.widget.setLayout(QHBoxLayout())
        
        for i in range(0, onargs):
            bw = widgetsource(otype, options, *args, widgetsource=widgetsource, **kwargs)
        
    def setValue(self, value):
        return super().setValue(value)
    
    def getValue(self):
        return super().getValue()