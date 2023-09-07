from __future__ import annotations
import typing as t
from qt_collapsible_section import Section
import click
from PySide6.QtWidgets import QLabel, QFrame, QWidget
from clickqt.widgets.basewidget import BaseWidget


class OptionGroupTitleWidget(BaseWidget):
    widget_type = Section

    def __init__(
        self,
        otype: click.ParamType,
        param: click.Parameter,
        parent: t.Optional["BaseWidget"] = None,
        **kwargs,
    ):
        super().__init__(otype, param, **kwargs)
        self.widget_name = param._GroupTitleFakeOption__group.__dict__["_name"]
        self.widget.setTitle(self.widget_name)
        self.groups = kwargs.get("opt_groups").get(self.widget_name)
        self.control_instance = kwargs.get("control")
        self.key = kwargs.get("key")
        self.label = QLabel(f"<b>{self.widget_name}</b>")
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)

        for i in range(self.layout.count() - 1):
            self.layout.itemAt(i).widget().close()

        self.layout.addWidget(self.line)

    def create_widget(self) -> QWidget:
        return self.widget_type()

    def get_widget_value(self) -> t.Any:
        return ""

    def set_value(self, value: t.Any):
        pass

    def get_widget_value_cmdline(self) -> str:
        return ""
