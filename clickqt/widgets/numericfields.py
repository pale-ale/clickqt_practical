from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox
from clickqt.widgets.basewidget import NumericField, BaseWidget
from click import Parameter, IntRange, FloatRange, ParamType
from typing import Any
import sys

class IntField(NumericField):
    widget_type = QSpinBox

    def __init__(self, otype:ParamType, param:Parameter, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)
        
        if not isinstance(otype, IntRange):
            # QSpinBox is limited to [-2**31; 2**31 - 1], but sys.maxsize returns 2**63 - 1
            self.setMinimum(-2**31) # Default is 0
            self.setMaximum(2**31 - 1) # Default is 99
        else:
            if otype.min is not None:
                self.setMinimum(otype.min)
            if otype.max is not None:
                self.setMaximum(otype.max)
        
        if self.parent_widget is None:
            self.setValue(BaseWidget.getParamDefault(param, 0))


class RealField(NumericField):
    widget_type = QDoubleSpinBox

    def __init__(self, otype:ParamType, param:Parameter, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        if not isinstance(otype, FloatRange):
            self.setMinimum(-sys.float_info.max) # Default is 0.0
            self.setMaximum(sys.float_info.max) # Default is 99.0
        else:
            if otype.min is not None:
                self.setMinimum(otype.min)
            if otype.max is not None:
                self.setMaximum(otype.max)

        if self.parent_widget is None:
            self.setValue(BaseWidget.getParamDefault(param, 0.0))
