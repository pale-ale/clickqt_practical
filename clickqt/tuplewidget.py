from PyQt6.QtWidgets import QWidget
from clickqt.base_widget import BaseWidget
from click import Parameter
from typing import Callable, Any

class TupleWidget(BaseWidget):
    widget_type = QWidget

    def __init__(self, options, *args, o:Any=None, widgetsource:Callable[[Any], BaseWidget]=None, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.children = []
        assert widgetsource
        assert o
        assert isinstance(o, Parameter)
        for t in o.type.types:
            bw = widgetsource(t, options)
            assert isinstance(bw, BaseWidget)
            bw.layout.removeWidget(bw.label)
            self.layout.addWidget(bw.container)
            self.children.append(bw)
    
    def setValue(self, value):
        assert len(value) == len(self.children)
        for i,c in enumerate(self.children):
            c.setValue(value[i])

    def getValue(self):
        return (c.getValue() for c in self.children)
