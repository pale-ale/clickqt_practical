from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QIcon, QAction
from clickqt.widgets.textfield import TextField
from click import Parameter, ParamType

class PasswordField(TextField):
    widget_type = QLineEdit

    def __init__(self, otype:ParamType, param:Parameter, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        assert hasattr(param, "hide_input") and param.hide_input, "'param.hide_input' should be True"

        self.widget.setEchoMode(QLineEdit.EchoMode.Password)

        self.show_hide_action = QAction(QIcon('clickqt\\images\\eye-show.png'), 'Show password')
        self.widget.addAction(self.show_hide_action, QLineEdit.ActionPosition.TrailingPosition)
        self.show_hide_action.setCheckable(True)

        def showPassword(show):
            if show:
                self.widget.setEchoMode(QLineEdit.EchoMode.Normal)
                self.show_hide_action.setIcon(QIcon('clickqt\\images\\eye-hide.png'))
                self.show_hide_action.setText('Hide password')
            else:
                self.widget.setEchoMode(QLineEdit.EchoMode.Password)
                self.show_hide_action.setIcon(QIcon('clickqt\\images\\eye-show.png'))
                self.show_hide_action.setText('Show password')

        self.show_hide_action.toggled.connect(showPassword)

