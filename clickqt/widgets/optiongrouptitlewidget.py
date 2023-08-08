from __future__ import annotations
import typing as t
import click
from PySide6.QtWidgets import QLabel, QFrame
from clickqt.widgets.basewidget import BaseWidget


class OptionGroupTitleWidget(BaseWidget):
    widget_type = QLabel

    def __init__(self, otype: click.ParamType, param: click.Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)
        self.widget_name = param._GroupTitleFakeOption__group.__dict__["_name"]
        self.label = QLabel(f"<b>{self.widget_name}</b>")
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        for i in range(self.layout.count()):
            self.layout.itemAt(i).widget().close()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line)

    def get_widget_value(self) -> t.Any:
        return ""

    def set_value(self, value: t.Any):
        pass
