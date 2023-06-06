from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, QEvent
from clickqt.core.error import ClickQtError
import sys

class FocusOutValidator(QWidget):
    """
        Validates a widget value when the widget gets out of focus
    """

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
            #else:
            #    print(err.message(), file=sys.stderr)

            self.widget.handleValid(err.type == ClickQtError.ErrorType.NO_ERROR)

        return QWidget.eventFilter(self, watched, event)
    