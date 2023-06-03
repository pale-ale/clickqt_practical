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

        if hasattr(kwargs.get("o"), "confirmation_prompt") and kwargs["o"].confirmation_prompt:
            kwargs["o"].confirmation_prompt = False  # Stop recursion
            kwargs["label"] = "Confirmation "
            self.confirmationField = PasswordField(options, *args, **kwargs)
            temp = self.container
            self.container = QWidget()
            self.vLayout = QVBoxLayout()
            self.vLayout.addWidget(temp)
            self.vLayout.addWidget(self.confirmationField.container)
            self.container.setLayout(self.vLayout)

            def onValueChanged():
                if self.getWidgetValue() != self.confirmationField.getWidgetValue():
                    self.confirmationField.widget.setStyleSheet("border: 1px solid red")
                    self.widget.setStyleSheet("border: 1px solid red")
                else: # Reset the border color
                    self.confirmationField.widget.setStyleSheet("")
                    self.widget.setStyleSheet("")

            self.confirmationField.widget.textChanged.connect(onValueChanged)
            self.widget.textChanged.connect(onValueChanged)

    def setValue(self, value: str):
        self.widget.setText(value)

    def getValue(self) -> Tuple[str, ClickQtError]:
        value, err = self.callback_validate()
        if err.type != ClickQtError.ErrorType.NO_ERROR:
            self.handleValid(False)
            return (value, err)
        
        if(hasattr(self, "confirmationField")):
            return self.getWidgetValue(), ClickQtError(ClickQtError.ErrorType.CONFIRMATION_INPUT_NOT_EQUAL_ERROR, self.widget_name) \
                if self.getWidgetValue() != self.confirmationField.getWidgetValue() else ClickQtError()
        else:
            return self.getWidgetValue(), ClickQtError()
        
    def getWidgetValue(self) -> str:
        return self.widget.text()
   