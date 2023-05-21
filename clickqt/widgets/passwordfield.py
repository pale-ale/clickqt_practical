from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget
from clickqt.widgets.textfield import TextField
from typing import Tuple
from clickqt.core.error import ClickQtError

class PasswordField(TextField):
    widget_type = QLineEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.widget.setEchoMode(QLineEdit.EchoMode.Password)

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
                if self.widget.text() != self.confirmationField.widget.text():
                    self.confirmationField.widget.setStyleSheet("border: 2px solid red")
                    self.widget.setStyleSheet("border: 2px solid red")
                else: # Reset the border color
                    self.confirmationField.widget.setStyleSheet("")
                    self.widget.setStyleSheet("")

            self.confirmationField.widget.textChanged.connect(onValueChanged)
            self.widget.textChanged.connect(onValueChanged)

    def setValue(self, value: str):
        self.widget.setText(value)

    def getValue(self) -> Tuple[str, ClickQtError]:
        if(hasattr(self, "confirmationField")):
            return self.widget.text(), ClickQtError.CONFIRMATION_INPUT_NOT_EQUAL_ERROR \
                if self.widget.text() != self.confirmationField.widget.text() else ClickQtError.NO_ERROR
        else:
            return self.widget.text(), ClickQtError.NO_ERROR
   