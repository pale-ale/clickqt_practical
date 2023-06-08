from PySide6.QtWidgets import QGroupBox, QHBoxLayout
from clickqt.widgets.base_widget import BaseWidget
from typing import Callable, Any
from click import Parameter, Tuple as ClickTuple

class TupleWidget(BaseWidget):
    widget_type = QGroupBox

    def __init__(self, param:Parameter, widgetsource:Callable[[Any], BaseWidget], *args, parent: BaseWidget=None, recinfo:list=None, **kwargs):
        if not isinstance(self.param.type, ClickTuple):
            raise TypeError
        if not self.param.type.is_composite:
            raise TypeError
        if not isinstance(self.param.type.types, list):
            raise TypeError
        
        super().__init__(param, parent, *args, **kwargs)
        self.children:list[BaseWidget] = []
        recinfo = recinfo if recinfo else []
        self.widget.setLayout(QHBoxLayout())


        for i,t in enumerate(TupleWidget.getTypesRecursive(self.param.type.types, recinfo)):
            recinfo.append(i)
            param.nargs = 0
            bw = widgetsource(t, param, *args, widgetsource=widgetsource, parent=self, recinfo=recinfo, **kwargs)
            recinfo.pop()
            bw.layout.removeWidget(bw.label)
            bw.label.deleteLater()
            self.widget.layout().addWidget(bw.container)
            self.children.append(bw)
    
    @staticmethod
    def getTypesRecursive(o:list|ClickTuple, recinfo:list):
        optiontype = o
        for i in recinfo:
            optiontype = optiontype[i]
        yield from optiontype.types if hasattr(optiontype, "types") else optiontype
    
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
    
    def getWidgetValue(self) -> list[Any]:
        return [c.getWidgetValue() for c in self.children]
