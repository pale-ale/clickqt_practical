from PySide6.QtWidgets import QDateTimeEdit
from PySide6.QtCore import QDateTime
from clickqt.widgets.base_widget import BaseWidget


class DateTimeEdit(BaseWidget):
    widget_type = QDateTimeEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

    def setValue(self, value: QDateTime):
        self.widget.setDateTime(value)
    
    def getWidgetValue(self) -> QDateTime:
        return self.widget.dateTime()
