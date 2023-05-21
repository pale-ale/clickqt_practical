from PySide6.QtWidgets import QDateTimeEdit
from PySide6.QtCore import QDateTime
from clickqt.widgets.base_widget import BaseWidget
from typing import Tuple
from clickqt.core.error import ClickQtError


class DateTimeEdit(BaseWidget):
    widget_type = QDateTimeEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

    def setValue(self, value):
        raise NotImplementedError

    def getValue(self) -> Tuple[QDateTime, ClickQtError]:
        return self.widget.dateTime(), ClickQtError.NO_ERROR
