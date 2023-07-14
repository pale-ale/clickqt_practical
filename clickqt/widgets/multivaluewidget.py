from PySide6.QtWidgets import QGroupBox, QVBoxLayout
from clickqt.widgets.basewidget import BaseWidget, MultiWidget
from click import Parameter, ParamType
from typing import Any, Callable, Optional

class MultiValueWidget(MultiWidget):
    widget_type = QGroupBox
    
    def __init__(self, otype:ParamType, param:Parameter, widgetsource:Callable[[Any], BaseWidget], parent:Optional[BaseWidget]=None, **kwargs):
        super().__init__(otype, param, parent=parent, **kwargs)

        assert param.nargs >= 2, f"'param.nargs' should be >= 2, but is '{param.nargs}'."

        self.widget.setLayout(QVBoxLayout())

         # Add param.nargs widgets of type otype
        for i in range(param.nargs):
            nargs = param.nargs
            param.nargs = 1 # Stop recursion
            bw:BaseWidget = widgetsource(otype, param, widgetsource=widgetsource, parent=self,**kwargs)
            param.nargs = nargs # click needs the right value for a correct conversion
            bw.layout.removeWidget(bw.label)
            bw.label.deleteLater()
            self.widget.layout().addWidget(bw.container)
            self.children.append(bw)

        self.init()
    