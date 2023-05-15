from PyQt6.QtWidgets import QSpinBox, QDoubleSpinBox
from clickqt.base_widget import NumericField
import sys

class IntField(NumericField):
    widget_type = QSpinBox

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        #QSpinBox is limited to [-2**31; 2**31 - 1], but sys.maxsize returns 2**63 - 1
        self.setMinimum(options.get("type").get("min") if options.get("type").get("min") is not None else -2**31)
        self.setMaximum(options.get("type").get("max") or 2**31 - 1)

class RealField(NumericField):
    widget_type = QDoubleSpinBox

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.setMinimum(options.get("type").get("min") if options.get("type").get("min") is not None else -sys.float_info.max)
        self.setMaximum(options.get("type").get("max") or sys.float_info.max) 
        