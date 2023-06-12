from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget
from PySide6.QtGui import QIcon, QAction
from clickqt.widgets.textfield import TextField
from typing import Tuple
from clickqt.core.error import ClickQtError
from click import Parameter

class PasswordField(TextField):
    widget_type = QLineEdit

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)

        self.widget.setEchoMode(QLineEdit.EchoMode.Password)

        self.show_hide_action = QAction(QIcon('clickqt\\images\\eye-show.png'), 'Show password')
        self.widget.addAction(self.show_hide_action, QLineEdit.ActionPosition.TrailingPosition)
        self.show_hide_action.setCheckable(True)

        def showPassword(show):
            self.widget.setEchoMode(QLineEdit.EchoMode.Normal if show else QLineEdit.EchoMode.Password)
            self.show_hide_action.setIcon(QIcon('clickqt\\images\\eye-hide.png') if show else QIcon('clickqt\\images\\eye-show.png'))

        self.show_hide_action.toggled.connect(showPassword)

        if hasattr(self.param, "confirmation_prompt") and self.param.confirmation_prompt:
            self.param.confirmation_prompt = False  # Stop recursion
            kwargs["label"] = "Confirmation "
            self.confirmation_field = PasswordField(param, *args, **kwargs)
            self.confirmation_field.confirmation_field = self
            temp = self.container
            self.container = QWidget()
            self.vLayout = QVBoxLayout()
            self.vLayout.addWidget(temp)
            self.vLayout.addWidget(self.confirmation_field.container)
            self.container.setLayout(self.vLayout)

    def setValue(self, value: str):
        self.widget.setText(value)

    def handleValid(self, valid: bool):
        super().handleValid(valid)

        if hasattr(self, "confirmation_field"):
            super(TextField, self.confirmation_field).handleValid(valid)      

    def getValue(self) -> Tuple[str, ClickQtError]:
        if hasattr(self, "confirmation_field"):
            val1, err1 = super().getValue()
            val2, err2 = super(TextField, self.confirmation_field).getValue()

            if err1.type != ClickQtError.ErrorType.NO_ERROR or err2.type != ClickQtError.ErrorType.NO_ERROR:
                return (None, err1 if err1.type != ClickQtError.ErrorType.NO_ERROR else err2)

            if val1 != val2:
                self.handleValid(False) # Update textfield border because super().getValue() doesn't do it here correctly
                return (None, ClickQtError(ClickQtError.ErrorType.CONFIRMATION_INPUT_NOT_EQUAL_ERROR, self.widget_name))
            else:
                self.handleValid(True)
                return (val1, ClickQtError())  
        else:
            return super().getValue()
        
    def getWidgetValue(self) -> str:
        return self.widget.text()
   