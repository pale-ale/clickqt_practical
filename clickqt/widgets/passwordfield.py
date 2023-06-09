from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget
from PySide6.QtGui import QIcon, QAction
from clickqt.widgets.textfield import TextField
from typing import Tuple
from clickqt.core.error import ClickQtError

class PasswordField(TextField):
    widget_type = QLineEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.widget.setEchoMode(QLineEdit.EchoMode.Password)

        self.show_hide_action = QAction(QIcon('clickqt\\images\\eye-show.png'), 'Show password')
        self.widget.addAction(self.show_hide_action, QLineEdit.ActionPosition.TrailingPosition)
        self.show_hide_action.setCheckable(True)

        def showPassword(show):
            self.widget.setEchoMode(QLineEdit.EchoMode.Normal if show else QLineEdit.EchoMode.Password)
            self.show_hide_action.setIcon(QIcon('clickqt\\images\\eye-hide.png') if show else QIcon('clickqt\\images\\eye-show.png'))

        self.show_hide_action.toggled.connect(showPassword)

    def setValue(self, value: str):
        self.widget.setText(value)
        
    def getWidgetValue(self) -> str:
        return self.widget.text()
   