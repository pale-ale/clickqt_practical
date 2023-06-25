from PySide6.QtWidgets import QDateTimeEdit
from PySide6.QtCore import QDateTime
from clickqt.widgets.basewidget import BaseWidget
from click import Parameter, ParamType
from typing import Any


class DateTimeEdit(BaseWidget):
    widget_type = QDateTimeEdit

    def __init__(self, otype:ParamType, param:Parameter, default:Any, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        if default is not None:
            self.setValue(default)

    def setValue(self, value: str):
        if isinstance(value, str):
            self.widget.setDateTime(QDateTime.fromString(value, "yyyy-MM-dd hh:mm:ss"))
    
    def getWidgetValue(self) -> str:
         # click.DateTime wants a str in form of '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S'or '%Y-%m-%d %H:%M:%S'
         # See https://click.palletsprojects.com/en/8.1.x/api/#click.DateTime
        return self.widget.dateTime().toString("yyyy-MM-dd hh:mm:ss")
