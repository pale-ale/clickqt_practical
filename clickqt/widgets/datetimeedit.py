from PySide6.QtWidgets import QDateTimeEdit
from PySide6.QtCore import QDateTime
from clickqt.widgets.base_widget import BaseWidget
from click import Parameter


class DateTimeEdit(BaseWidget):
    widget_type = QDateTimeEdit

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)

    def setValue(self, value: QDateTime):
        self.widget.setDateTime(value)
    
    def getWidgetValue(self) -> str:
         # click.DateTime wants a str in form of '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S'or '%Y-%m-%d %H:%M:%S'
         # See https://click.palletsprojects.com/en/8.1.x/api/#click.DateTime
        return self.widget.dateTime().toString("yyyy-MM-dd hh:mm:ss")
