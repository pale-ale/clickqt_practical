from PySide6.QtWidgets import QGroupBox, QHBoxLayout
from clickqt.widgets.base_widget import BaseWidget
from typing import Callable, Any

class TupleWidget(BaseWidget):
    widget_type = QGroupBox

    def __init__(self, options, widgetsource:Callable[[Any], BaseWidget]=None, recinfo:list=None, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.children = []
        recinfo = recinfo if recinfo else []
        self.widget.setLayout(QHBoxLayout())

        for i,t in enumerate(TupleWidget.getTypesRecursive(self.click_object.type.types, recinfo)):
            recinfo.append(i)
            bw = widgetsource(t, options, widgetsource=widgetsource, recinfo=recinfo, *args, **kwargs)
            recinfo.pop()
            bw.layout.removeWidget(bw.label)
            bw.label.deleteLater()
            self.widget.layout().addWidget(bw.container)
            self.children.append(bw)
    
    @staticmethod
    def getTypesRecursive(o, recinfo):
        optiontype = o
        for i in recinfo:
            optiontype = optiontype[i]
        yield from optiontype.types if hasattr(optiontype, "types") else optiontype
    
    def setValue(self, value):
        assert len(value) == len(self.children)
        for i,c in enumerate(self.children):
            c.setValue(value[i])
    
    def getWidgetValue(self) -> str:
        return [c.getWidgetValue() for c in self.children]
