from __future__ import annotations
import typing as t
import click
from PySide6.QtCore import (
    QPropertyAnimation,
    Qt,
    QParallelAnimationGroup,
    QAbstractAnimation,
)
from PySide6.QtWidgets import QLabel, QFrame, QToolButton
from clickqt.widgets.basewidget import BaseWidget


class OptionGroupTitleWidget(BaseWidget):
    widget_type = QLabel

    def __init__(
        self,
        otype: click.ParamType,
        param: click.Parameter,
        parent: t.Optional["BaseWidget"] = None,
        **kwargs,
    ):
        super().__init__(otype, param, **kwargs)
        self.widget_name = param._GroupTitleFakeOption__group.__dict__["_name"]
        self.label = QLabel(f"<b>{self.widget_name}</b>")
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)

        self.toggle_button = QToolButton(text="Toggle", checkable=True, checked=False)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)

        self.toggle_button.pressed.connect(self.toggle_option_group)

        for i in range(self.layout.count()):
            self.layout.itemAt(i).widget().close()
        self.layout.addWidget(self.label)
        if (
            isinstance(param, click.Option)
            and param.help
            and (parent is None or kwargs.get("vboxlayout"))
        ):  # Help text
            self.help_label = QLabel(text=param.help)
            self.help_label.setWordWrap(True)  # Multi-line
            self.layout.addWidget(self.help_label)
        self.layout.addWidget(self.toggle_button)
        self.layout.addWidget(self.line)

    def get_widget_value(self) -> t.Any:
        return ""

    def set_value(self, value: t.Any):
        pass

    def get_widget_value_cmdline(self) -> str:
        return ""

    def toggle_option_group(self):
        # Get the current state of the button before toggling
        print(f"State of the button itself: {self.toggle_button.isChecked()}")
        current_checked_state = self.toggle_button.isChecked()
        print(f"Current_checked_state: {current_checked_state}")
        # Toggle the button state
        self.toggle_button.setChecked(not current_checked_state)
        print(f"State of button itself after: {self.toggle_button.isChecked()}")

        # Update the arrow type based on the new state
        if self.toggle_button.isChecked():
            target_arrow_type = Qt.DownArrow
        else:
            target_arrow_type = Qt.RightArrow

        self.update_arrow_icon(target_arrow_type)

        click.echo("Toggleable")

    def update_arrow_icon(self, arrow_type):
        self.toggle_button.setArrowType(arrow_type)
