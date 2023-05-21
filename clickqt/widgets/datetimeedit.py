from PySide6.QtWidgets import QDateTimeEdit
from clickqt.widgets.base_widget import BaseWidget


class DateTimeEdit(BaseWidget):
    widget_type = QDateTimeEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

    def setValue(self, value):
        raise NotImplementedError

    def getValue(self):
        return self.widget.dateTime()
