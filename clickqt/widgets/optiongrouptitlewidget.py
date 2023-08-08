from __future__ import annotations
import typing as t
import click
from PySide6.QtWidgets import QLabel
from clickqt.widgets.basewidget import BaseWidget


class OptionGroupTitleWidget(BaseWidget):
    widget_type = QLabel
    i: int

    def __init__(self, otype: click.ParamType, param: click.Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)
        self.widget_name = kwargs.get("title")
        self.label = QLabel(f"<b>{self.widget_name}</b>")
        self.widget.setObjectName(self.widget_name)
        for i in range(self.layout.count()):
            self.layout.itemAt(i).widget().close()
        self.layout.addWidget(self.label)

    def get_widget_value(self) -> t.Any:
        return None

    def set_value(self, value: t.Any):
        pass
