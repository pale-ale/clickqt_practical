from PySide6.QtWidgets import QDateTimeEdit
from PySide6.QtCore import QDateTime
from clickqt.widgets.basewidget import BaseWidget
from click import Parameter, ParamType, Context, DateTime
from typing import Any


class DateTimeEdit(BaseWidget):
    widget_type = QDateTimeEdit

    def __init__(self, otype:ParamType, param:Parameter, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        assert isinstance(otype, DateTime), f"'otype' must be of type '{DateTime}', but is '{type(otype)}'."

        self.widget.setDisplayFormat("dd.MM.yyyy hh:mm:ss")

        if self.parent_widget is None and (default := BaseWidget.getParamDefault(param, None)) is not None:
            self.setValue(default)

    def setValue(self, value:Any):
        self.widget.setDateTime(QDateTime.fromString(str(self.type.convert(str(value), self.click_command, Context(self.click_command))), "yyyy-MM-dd hh:mm:ss"))
    
    def getWidgetValue(self) -> str:
        # click.DateTime wants a str in form of '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S' or user defined format
        # See https://click.palletsprojects.com/en/8.1.x/api/#click.DateTime
        return self.widget.dateTime().toPython().strftime(self.type.formats[-1]) # Convert the string into the last added format in formats-list (default: %Y-%m-%d %H:%M:%S)

