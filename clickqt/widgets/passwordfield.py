from __future__ import annotations

import click
from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QIcon, QAction

from clickqt.widgets.textfield import TextField


class PasswordField(TextField):
    """Represents a click.types.StringParamType-object with hide_input==True.
    The input will be hidden by default, but can be made visible by clicking on the "eye-show" icon.

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QLineEdit  #: The Qt-type of this widget.

    def __init__(self, otype: click.ParamType, param: click.Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert (
            hasattr(param, "hide_input") and param.hide_input
        ), "'param.hide_input' should be True"

        self.icon_text = (
            (QIcon("clickqt\\images\\eye-show.png"), "Show password"),
            (QIcon("clickqt\\images\\eye-hide.png"), "Hide password"),
        )
        self.show_hide_action = QAction(
            icon=self.icon_text[0][0], text=self.icon_text[0][1]
        )
        self.widget.setEchoMode(QLineEdit.EchoMode.Password)
        self.widget.addAction(
            self.show_hide_action, QLineEdit.ActionPosition.TrailingPosition
        )
        self.show_hide_action.setCheckable(True)

        def show_password(show):
            self.widget.setEchoMode(
                QLineEdit.EchoMode.Normal if show else QLineEdit.EchoMode.Password
            )
            self.show_hide_action.setIcon(self.icon_text[show][0])
            self.show_hide_action.setText(self.icon_text[show][1])

        self.show_hide_action.toggled.connect(show_password)
