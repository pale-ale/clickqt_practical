import click
from PySide6.QtWidgets import QGroupBox, QVBoxLayout
from clickqt.widgets.base_widget import BaseWidget
from clickqt.widgets.numericfields import IntField, RealField
from clickqt.widgets.textfield import TextField
from typing import Any, List

class MultiValueWidget(BaseWidget):
    widget_type = QGroupBox
    
    def __init__(self, options, otype, onargs, parent: BaseWidget = None, *args, **kwargs):
        super().__init__(options, parent, *args, **kwargs)
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
                    bw = widgetclass(options, parent=self, *args, **kwargs)
                    bw.layout.removeWidget(bw.label)
                    bw.label.deleteLater()
                    self.widget.layout().addWidget(bw.container)
                    self.children.append(bw)
        
    def setValue(self, value):
        assert len(value) == len(self.children)
        for i,c in enumerate(self.children):
            c.setValue(value[i])

    def handleValid(self, valid: bool):
        for c in self.children:
            BaseWidget.handleValid(c, valid)
    
    def getWidgetValue(self) -> List[Any]:
        return [c.getWidgetValue() for c in self.children]