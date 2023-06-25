from PySide6.QtWidgets import QGroupBox, QHBoxLayout
from clickqt.widgets.basewidget import BaseWidget
from typing import Callable, Any
from click import Parameter, Tuple as ClickTuple, Context, ParamType, BadParameter
from gettext import ngettext

class TupleWidget(BaseWidget):
    widget_type = QGroupBox

    def __init__(self, otype:ParamType, param:Parameter, widgetsource:Callable[[Any], BaseWidget], *args, parent:BaseWidget|None=None, **kwargs):
        if not isinstance(otype, ClickTuple):
            raise TypeError
        if not otype.is_composite:
            raise TypeError
        if not isinstance(otype.types, list):
            raise TypeError
        
        super().__init__(otype, param, *args, parent=parent, **kwargs)
        self.children:list[BaseWidget] = []

        self.widget.setLayout(QHBoxLayout())

        for i,t in enumerate(otype.types if hasattr(otype, "types") else otype):
            nargs = self.param.nargs
            self.param.nargs = 0
            bw:BaseWidget = widgetsource(t, self.param, *args, widgetsource=widgetsource, parent=self, **kwargs)
            self.param.nargs = nargs 
            bw.layout.removeWidget(bw.label)
            bw.label.deleteLater()
            self.widget.layout().addWidget(bw.container)
            self.children.append(bw)

        if self.parent_widget is None:
            # Consider envvar
            if (envvar_values := self.param.resolve_envvar_value(Context(self.click_command))) is not None:
                self.setValue(self.type.split_envvar_value(envvar_values))
            elif (default := BaseWidget.getParamDefault(param, None)) is not None: # Consider default value
                self.setValue(default)
    
    def setValue(self, value):
        if len(value) != self.param.nargs:
            raise BadParameter(ngettext("Takes {nargs} values but 1 was given.", "Takes {nargs} values but {len} were given.",len(value))
                               .format(nargs=self.param.nargs, len=len(value)),
                               ctx=Context(self.click_command),
                               param=self.param)
        
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
