from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox
from clickqt.widgets.basewidget import NumericField, BaseWidget
from click import Parameter, IntRange, FloatRange, ParamType, INT, FLOAT
import sys

class IntField(NumericField):
    widget_type = QSpinBox

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert isinstance(otype, IntRange|type(INT)), f"'otype' must be of type '{IntRange}' or '{type(INT)}', but is '{type(otype)}'."
        
        if not isinstance(otype, IntRange):
            # QSpinBox is limited to [-2**31; 2**31 - 1], but sys.maxsize returns 2**63 - 1
            self.setMinimum(-2**31) # Default is 0
            self.setMaximum(2**31 - 1) # Default is 99
        else:
            if otype.min is not None:
                self.setMinimum(otype.min + (1 if otype.min_open else 0))
            if otype.max is not None:
                self.setMaximum(otype.max - (1 if otype.max_open else 0))
        
        if self.parent_widget is None:
            self.setValue(BaseWidget.getParamDefault(param, 0))


class RealField(NumericField):
    widget_type = QDoubleSpinBox

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert isinstance(otype, FloatRange|type(FLOAT)), f"'otype' must be of type '{FloatRange}' or '{type(FLOAT)}', but is '{type(otype)}'."

        if not isinstance(otype, FloatRange):
            self.setMinimum(-sys.float_info.max) # Default is 0.0
            self.setMaximum(sys.float_info.max) # Default is 99.0
        else:
            if otype.min is not None:
                self.setMinimum(otype.min + (10**-self.widget.decimals() if otype.min_open else 0.0))
            if otype.max is not None:
                self.setMaximum(otype.max - (10**-self.widget.decimals() if otype.max_open else 0.0))

        if self.parent_widget is None:
            self.setValue(BaseWidget.getParamDefault(param, 0.0))
