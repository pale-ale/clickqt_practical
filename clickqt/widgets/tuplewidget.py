from PySide6.QtWidgets import QGroupBox, QHBoxLayout
from clickqt.widgets.basewidget import BaseWidget
from typing import Callable, Any
from click import Parameter, Tuple as ClickTuple, Context, ParamType

class TupleWidget(BaseWidget):
    widget_type = QGroupBox

    def __init__(self, otype:ParamType, param:Parameter, default:Any, widgetsource:Callable[[Any], BaseWidget], *args, parent:BaseWidget|None=None, recinfo:list=None, **kwargs):
        if not isinstance(param.type, ClickTuple):
            raise TypeError
        if not param.type.is_composite:
            raise TypeError
        if not isinstance(param.type.types, list):
            raise TypeError
        
        super().__init__(otype, param, *args, parent=parent, **kwargs)
        self.children:list[BaseWidget] = []
        recinfo = recinfo if recinfo else []
        self.widget.setLayout(QHBoxLayout())

        for i,t in enumerate(TupleWidget.getTypesRecursive(self.param.type.types, recinfo)):
            recinfo.append(i)
            self.param.nargs = 0
            # defaults have to be considered after all widgets are constructed
            bw:BaseWidget = widgetsource(t, self.param, None, *args, widgetsource=widgetsource, parent=self, recinfo=recinfo, **kwargs)
            recinfo.pop()
            bw.layout.removeWidget(bw.label)
            bw.label.deleteLater()
            self.widget.layout().addWidget(bw.container)
            self.children.append(bw)

        if self.parent_widget is None:
            # Consider envvar
            if (envvar_value := self.param.resolve_envvar_value(Context(self.click_command))) is not None:
                self.setValue(self.type.split_envvar_value(envvar_value))
            elif default is not None: # Consider default value
                self.setValue(default)
    
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

    def isEmpty(self) -> bool:
        if len(self.children) == 0:
            return True

        for c in self.children:
            if c.isEmpty():
                return True
        
        return False
    
    def getWidgetValue(self) -> list[Any]:
        return [c.getWidgetValue() for c in self.children]
