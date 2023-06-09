from PySide6.QtWidgets import QGroupBox, QHBoxLayout
from clickqt.core.error import ClickQtError
from clickqt.widgets.base_widget import BaseWidget
from typing import Callable, Any
from click import Context, Parameter, Tuple as ClickTuple

class TupleWidget(BaseWidget):
    widget_type = QGroupBox

    def __init__(self, param:Parameter, widgetsource:Callable[[Any], BaseWidget], *args, parent: BaseWidget=None, recinfo:list=None, **kwargs):
        if not isinstance(param.type, ClickTuple):
            raise TypeError
        if not param.type.is_composite:
            raise TypeError
        if not isinstance(param.type.types, list):
            raise TypeError
        
        super().__init__(param, parent, *args, **kwargs)
        self.children:list[BaseWidget] = []
        recinfo = recinfo if recinfo else []
        self.widget.setLayout(QHBoxLayout())


        for i,t in enumerate(TupleWidget.getTypesRecursive(self.param.type.types, recinfo)):
            recinfo.append(i)
            self.param.nargs = 0
            bw = widgetsource(t, self.param, *args, widgetsource=widgetsource, parent=self, recinfo=recinfo, **kwargs)
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

    def getValue(self) -> tuple[Any, ClickQtError]:
        if self.parent_widget:
            return self.parent_widget.getValue()

        value = None
        try:
            value = self.param.type.convert(self.getWidgetValue(), None, None)
        except Exception as e:
            return (None, ClickQtError(ClickQtError.ErrorType.CONVERSION_ERROR, self.widget_name, e))
        
        try: # Consider callbacks 
            ret_val = (self.param.process_value(Context(self.click_command), value), ClickQtError())
            self.handleValid(True)
            return ret_val
        except Exception as e:
            self.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.CALLBACK_VALIDATION_ERROR, self.widget_name, e))
