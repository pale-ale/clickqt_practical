from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, QEvent
from clickqt.core.error import ClickQtError


class CallbackValidator(QWidget):
    def __init__(self, widget): # widget: BaseWidget (Can't import due to circular import)
        super().__init__()
        
        self.widget = widget

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.FocusOut:
            value, err = self.widget.getValue()
            if value is not None and err.type == ClickQtError.ErrorType.NO_ERROR:
                #TODO: Check if value has correct type
                #self.widget.setValue(value)
                pass

            self.widget.handleValid(err.type == ClickQtError.ErrorType.NO_ERROR)

        return QWidget.eventFilter(self, watched, event)
    