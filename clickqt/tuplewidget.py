from PyQt6.QtWidgets import QGroupBox, QHBoxLayout
from clickqt.base_widget import BaseWidget
from click import Parameter
from typing import Callable, Any

class TupleWidget(BaseWidget):
    widget_type = QGroupBox

    def __init__(self, options, *args, o:Parameter=None, widgetsource:Callable[[Any], BaseWidget]=None, recinfo:list=None, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.children = []
        recinfo = recinfo if recinfo else []
        self.widget.setLayout(QHBoxLayout())

        for i,t in enumerate(TupleWidget.getTypesRecursive(o.type.types, recinfo)):
            recinfo.append(i)
            bw = widgetsource(t, options, *args, o=o, widgetsource=widgetsource, recinfo=recinfo, **kwargs)
            recinfo.pop()
            bw.layout.removeWidget(bw.label)
            self.widget.layout().addWidget(bw.container)
            self.children.append(bw)
    
    @staticmethod
    def getTypesRecursive(o, recinfo):
        print(recinfo)
        optiontype = o
        for i in recinfo:
            optiontype = optiontype[i]
        yield from optiontype.types if hasattr(optiontype, "types") else optiontype
    
    def setValue(self, value):
        assert len(value) == len(self.children)
        for i,c in enumerate(self.children):
            c.setValue(value[i])

    def getValue(self):
        return (c.getValue() for c in self.children)
