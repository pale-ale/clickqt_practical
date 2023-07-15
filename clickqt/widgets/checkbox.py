from PySide6.QtWidgets import QCheckBox
from clickqt.widgets.basewidget import BaseWidget
from click import Parameter, Context, ParamType, BOOL
from typing import Any

class CheckBox(BaseWidget):
    """Represents a click.types.BoolParamType object.
    
    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for 
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QCheckBox #: The Qt-type of this widget.

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert isinstance(otype, type(BOOL)), f"'otype' must be of type '{type(BOOL)}', but is '{type(otype)}'."

        if self.parent_widget is None:
            self.setValue(BaseWidget.getParamDefault(param, False))
        
    def setValue(self, value:Any):
        self.widget.setChecked(bool(self.type.convert(str(value), self.click_command, Context(self.click_command))))
    
    def getWidgetValue(self) -> bool:
        return self.widget.isChecked()
    