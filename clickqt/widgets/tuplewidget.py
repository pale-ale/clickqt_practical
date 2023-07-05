from PySide6.QtWidgets import QGroupBox, QHBoxLayout
from clickqt.widgets.basewidget import BaseWidget, MultiWidget
from typing import Callable, Any
from click import Parameter, ParamType, Tuple as ClickTuple 


class TupleWidget(MultiWidget):
    widget_type = QGroupBox

    def __init__(self, otype:ParamType, param:Parameter, widgetsource:Callable[[Any], BaseWidget], *args, parent:BaseWidget|None=None, **kwargs):
        super().__init__(otype, param, *args, parent=parent, **kwargs)
        
        assert isinstance(otype, ClickTuple), f"'otype' must be of type '{ClickTuple}', but is '{type(otype)}'."
        assert otype.is_composite, f"otype.is_composite should be True"

        self.widget.setLayout(QHBoxLayout())

        for t in (otype.types if hasattr(otype, "types") else otype):
            nargs = self.param.nargs
            self.param.nargs = 1
            bw:BaseWidget = widgetsource(t, self.param, *args, widgetsource=widgetsource, parent=self, **kwargs)
            self.param.nargs = nargs 
            bw.layout.removeWidget(bw.label)
            bw.label.deleteLater()
            self.widget.layout().addWidget(bw.container)
            self.children.append(bw)

        self.init()
