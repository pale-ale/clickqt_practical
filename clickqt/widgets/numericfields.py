from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox
from clickqt.widgets.basewidget import NumericField, BaseWidget
from click import Parameter, IntRange, FloatRange, ParamType, INT, FLOAT
import sys

class IntField(NumericField):
    """Represents a click.types.IntParamType- and click.types.IntRange-object.
    If the click object is of type `click.types.IntParamType`, the minimum will be set to -2**31 and the maximum to 2**31 - 1.
    In the other case, the minimum and maximum are defined by clicks range options.
    
    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('widgetsource', 'parent', 'com', 'label') needed for 
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QSpinBox #: The Qt-type of this widget.

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert isinstance(otype, (IntRange,type(INT))), f"'otype' must be of type '{IntRange}' or '{type(INT)}', but is '{type(otype)}'."
        
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
    """Represents a click.types.FloatParamType- and click.types.FloatRange-object. Two decimals will be displayed by default.
    If the click object is of type `click.types.FloatParamType`, the minimum will be set to -sys.float_info.max and the maximum to sys.float_info.max.
    In the other case, the minimum and maximum are defined by clicks range options.
    
    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('widgetsource', 'parent', 'com', 'label') needed for 
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QDoubleSpinBox #: The Qt-type of this widget.

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert isinstance(otype, (FloatRange,type(FLOAT))), f"'otype' must be of type '{FloatRange}' or '{type(FLOAT)}', but is '{type(otype)}'."

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
