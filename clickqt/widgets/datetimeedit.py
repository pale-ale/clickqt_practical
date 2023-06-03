from PySide6.QtWidgets import QDateTimeEdit
from PySide6.QtCore import QDateTime
from clickqt.widgets.base_widget import BaseWidget
from typing import Tuple
from clickqt.core.error import ClickQtError


class DateTimeEdit(BaseWidget):
    widget_type = QDateTimeEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

    def setValue(self, value: QDateTime):
        self.widget.setDateTime(value)

    def getValue(self) -> Tuple[QDateTime, ClickQtError]:
        value, err = self.callback_validate()
        if err.type != ClickQtError.ErrorType.NO_ERROR:
            self.handleValid(False)
            return (value, err)
        
        return (self.getWidgetValue(), ClickQtError())
    
    def getWidgetValue(self) -> QDateTime:
        return self.widget.dateTime()
