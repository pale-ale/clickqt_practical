from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, QEvent
from clickqt.core.error import ClickQtError
from clickqt.widgets.base_widget import BaseWidget
from clickqt.widgets.nvaluewidget import NValueWidget
from click import Context
from typing import Tuple, Any
import sys
from io import BytesIO, TextIOWrapper 

class FocusOutValidator(QWidget):
    """
        Validates a widget value when the widget goes out of focus
    """

    def __init__(self, widget: BaseWidget):
        super().__init__()
        
        self.widget = widget

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.FocusOut:
            # Don't print callback prints
            old_strerr = sys.stderr
            old_strout = sys.stdout
            sys.stderr = sys.stdout = TextIOWrapper(BytesIO(), "utf-8")

            # Don't set the new value because the callback call could reject the (new) value
            # when trying to execute the command (=user clicked on the "Run"-button) 
            self.__validate(self.widget) 

            sys.stderr = old_strerr
            sys.stdout = old_strout

        return QWidget.eventFilter(self, watched, event)
    
    def __validate(self, widget: BaseWidget) -> Tuple[Any, ClickQtError]:
        """
            Validates the value of the widget, which went out of focus
        """
        if widget.parent_widget is not None and not isinstance(widget.parent_widget, NValueWidget):
            return self.__val(widget)
        elif widget.parent_widget is None:
            return widget.getValue()

        # self.widget.parent_widget == NValueWidget -> We have a child here

        try: # Try to convert the provided value into the corresponding click object type
            ret_val = widget.param.type.convert(value=widget.getWidgetValue(), param=widget.param, ctx=Context(widget.click_command))
            # Don't consider callbacks because we have only one child here
            widget.handleValid(True)
            return (ret_val, ClickQtError())
        except Exception as e:
            widget.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.CONVERTING_ERROR, widget.widget_name, e))

    def __val(self, widget: BaseWidget) -> Tuple[Any, ClickQtError]: 
        """
            Calls getValue() on the widget with no parent
        """
        if widget.parent_widget is not None:
            return self.__val(widget.parent_widget)
        return widget.getValue()