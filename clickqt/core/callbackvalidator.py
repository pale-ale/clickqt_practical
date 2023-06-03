import click
from typing import Any, Tuple
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, QEvent
from clickqt.core.error import ClickQtError


class CallbackValidator(QWidget):
    def __init__(self, command: click.Command, param: click.Option|click.Argument, widget):
        super().__init__()
        
        self.command = command
        self.param = param
        self.widget = widget

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.FocusOut:
            value, err = self.validate()
            if value is not None and err.type != ClickQtError.ErrorType.CALLBACK_VALIDATION_ERROR:
                #TODO: Check if value has correct type
                self.widget.setValue(value)
            self.widget.handleValid(err.type == ClickQtError.ErrorType.NO_ERROR)

        return QWidget.eventFilter(self, watched, event)
    
    def validate(self) -> Tuple[Any, ClickQtError]:
        try:
            return (self.param.callback(click.Context(self.command), self.param, self.widget.getWidgetValue()), ClickQtError())
        except click.BadParameter as e:
            return (None, ClickQtError(ClickQtError.ErrorType.CALLBACK_VALIDATION_ERROR, str(e)))
