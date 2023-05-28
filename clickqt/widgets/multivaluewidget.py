import click
from PySide6.QtWidgets import QGroupBox, QVBoxLayout
from clickqt.widgets.base_widget import BaseWidget
from clickqt.widgets.numericfields import IntField, RealField
from clickqt.core.error import ClickQtError
from clickqt.widgets.textfield import TextField
from typing import Any, List, Tuple

class MultiValueWidget(BaseWidget):
    widget_type = QGroupBox
    
    def __init__(self, options, otype, onargs, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.children = []
        self.widget.setLayout(QVBoxLayout())
        
        typedict = {
            click.types.IntParamType: IntField,
            click.types.FloatParamType: RealField,
            click.types.StringParamType: TextField,
        }
        
        for i in range(onargs):
            for t, widgetclass in typedict.items():
                if isinstance(otype, t):
                    bw = widgetclass(options)
                    bw.layout.removeWidget(bw.label)
                    self.widget.layout().addWidget(bw.container)
                    self.children.append(bw)
        
    def setValue(self, value):
        assert len(value) == len(self.children)
        for i,c in enumerate(self.children):
            c.setValue(value[i])

    def getValue(self) -> Tuple[List[Any], ClickQtError]:
        return ([c.getValue() for c in self.children], ClickQtError.NO_ERROR)