""" Contains the checkbox widget """
from __future__ import annotations

import typing as t

from PySide6.QtWidgets import QCheckBox
import click

from clickqt.widgets.basewidget import BaseWidget


class CheckBox(BaseWidget):
    """Represents a click.types.BoolParamType object.

    :param otype: The type which specifies the clickqt widget type.
        This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for
        :class:`~clickqt.widgets.basewidget.MultiWidget`- /
        :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`- widgets
    """

    widget_type = QCheckBox  #: The Qt-type of this widget.

    def __init__(self, otype: click.ParamType, param: click.Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert isinstance(
            otype, type(click.BOOL)
        ), f"'otype' must be of type '{type(click.BOOL)}', but is '{type(otype)}'."

        self.widget.setText("Enable")

        if self.parent_widget is None:
            self.set_value(BaseWidget.get_param_default(param, False))

    def set_value(self, value: t.Any):
        self.widget.setChecked(
            bool(
                self.type.convert(
                    str(value), self.click_command, click.Context(self.click_command)
                )
            )
        )

    def get_widget_value(self) -> bool:
        return self.widget.isChecked()
