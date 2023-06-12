from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox
from clickqt.widgets.base_widget import NumericField
from click import Parameter, IntRange, FloatRange


class IntField(NumericField):
    widget_type = QSpinBox

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)
        
        if not isinstance(param.type, IntRange):
            return
        if param.type.min is not None:
            self.setMinimum(param.type.min)
        if param.type.max is not None:
            self.setMaximum(param.type.max)


class RealField(NumericField):
    widget_type = QDoubleSpinBox

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)

        if not isinstance(param.type, FloatRange):
            return
        if param.type.min is not None:
            self.setMinimum(param.type.min)
        if param.type.max is not None:
            self.setMaximum(param.type.max)
