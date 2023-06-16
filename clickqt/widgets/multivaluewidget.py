import click
from PySide6.QtWidgets import QGroupBox, QVBoxLayout
from clickqt.widgets.base_widget import BaseWidget
from clickqt.widgets.numericfields import IntField, RealField
from clickqt.widgets.textfield import TextField
from clickqt.widgets.tuplewidget import TupleWidget
from click import Parameter
from typing import Any, List

class MultiValueWidget(BaseWidget):
    widget_type = QGroupBox
    
    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)
        self.children:list[BaseWidget] = []
        self.widget.setLayout(QVBoxLayout())
        
        typedict = {
            click.types.IntParamType: IntField,
            click.types.FloatParamType: RealField,
            click.types.StringParamType: TextField,
        }

        if param.nargs < 2:
            raise TypeError(f"param.nargs should be >= 2 when creating a MultiValueWIdget but is {param.nargs}.")
        
        for i in range(param.nargs):
            for t, widgetclass in typedict.items():
                if isinstance(param.type, t):
                    bw:BaseWidget = widgetclass(param, parent=self, *args, **kwargs)
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
            if not isinstance(c, TupleWidget):
                BaseWidget.handleValid(c, valid)
            else:
                c.handleValid(valid) # Recursive
    
    def getWidgetValue(self) -> List[Any]:
        return [c.getWidgetValue() for c in self.children]
    
    def getWidgetValueToString(self) -> str:
        return " ".join(self.getWidgetValue())