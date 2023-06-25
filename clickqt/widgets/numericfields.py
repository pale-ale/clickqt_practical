from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox
from clickqt.widgets.basewidget import NumericField, BaseWidget
from click import Parameter, IntRange, FloatRange, ParamType
from typing import Any
import sys

class IntField(NumericField):
    widget_type = QSpinBox

    def __init__(self, otype:ParamType, param:Parameter, default:Any, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)
        
        if not isinstance(param.type, IntRange):
            # QSpinBox is limited to [-2**31; 2**31 - 1], but sys.maxsize returns 2**63 - 1
            self.setMinimum(-2**31) # Default is 0
            self.setMaximum(2**31 - 1) # Default is 99
        else:
            if param.type.min is not None:
                self.setMinimum(param.type.min)
            if param.type.max is not None:
                self.setMaximum(param.type.max)
        
        self.setValue(default if default is not None else 0)


class RealField(NumericField):
    widget_type = QDoubleSpinBox

    def __init__(self, otype:ParamType, param:Parameter, default:Any, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        if not isinstance(param.type, FloatRange):
            self.setMinimum(-sys.float_info.max) # Default is 0.0
            self.setMaximum(sys.float_info.max) # Default is 99.0
        else:
            if param.type.min is not None:
                self.setMinimum(param.type.min)
            if param.type.max is not None:
                self.setMaximum(param.type.max)
    
        self.setValue(default if default is not None else 0.0)
