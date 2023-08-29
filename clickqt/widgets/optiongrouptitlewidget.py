from __future__ import annotations
import typing as t
import click
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QFrame, QToolButton, QHBoxLayout
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
        self.groups = kwargs.get("opt_groups").get(self.widget_name)
        self.control_instance = kwargs.get("control")
        self.key = kwargs.get("key")
        self.label = QLabel(f"<b>{self.widget_name}</b>")
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)

        self.toggle_button = QToolButton(checkable=True)
        self.toggle_button.setStyleSheet(
            """
            QToolButton {
                border: 1px solid #3498db;
                border-radius: 10px;
                padding: 2px 5px;
            }
            QToolButton:hover {
                background-color: #2980b9;
            }
        """
        )
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.DownArrow)

        self.toggle_button.pressed.connect(
            lambda: self.set_expanded(self.toggle_button.isChecked())
        )

        for i in range(self.layout.count()):
            self.layout.itemAt(i).widget().close()
        # Add a vertical layout to the existing horizontal layout for UI fix
        self.toggle_layout = QHBoxLayout()
        self.toggle_layout.addWidget(self.toggle_button)
        self.toggle_layout.addWidget(self.label)
        self.layout.addLayout(self.toggle_layout)
        if (
            isinstance(param, click.Option)
            and param.help
            and (parent is None or kwargs.get("vboxlayout"))
        ):  # Help text
            self.help_label = QLabel(text=param.help)
            self.help_label.setWordWrap(True)  # Multi-line
            self.layout.addWidget(self.help_label)
        self.layout.addWidget(self.line)

    def get_widget_value(self) -> t.Any:
        return ""

    def set_value(self, value: t.Any):
        pass

    def get_widget_value_cmdline(self) -> str:
        return ""

    def is_option_group_visible(self):
        """Function to determine if all the necessary widgets are already collapsed or not."""
        return not any(
            self.control_instance.widget_registry[self.key]
            .get(grouped_option)
            .is_collapsed
            for grouped_option in self.groups
        )

    def set_expanded(self, is_checked: bool):
        """Initiates the toggle action.
        :param is_checked: The bool indicating if the button has been checked or not.
        """
        # Update the arrow type based on the new state
        target_arrow_type = Qt.RightArrow if not is_checked else Qt.DownArrow

        self.update_arrow_icon(target_arrow_type, not is_checked)

    def update_arrow_icon(self, arrow_type: Qt.ArrowType, is_checked: bool):
        """
        Function to update the arrow status and is also responsible for hiding the widgets based on the current status.

        :param arrow_type: The arrow_direction one wants to display.

        :param is_checked: The bool indicating if the button has been checked or not.
        """
        self.toggle_button.setArrowType(arrow_type)
        for grouped_option in self.groups:
            self.control_instance.widget_registry[self.key].get(
                grouped_option
            ).container.setVisible(not is_checked)
