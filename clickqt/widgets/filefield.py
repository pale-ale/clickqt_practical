from PySide6.QtWidgets import QLineEdit, QPushButton, QFileDialog, QInputDialog,QDialogButtonBox
from clickqt.widgets.textfield import TextField
from typing import Tuple, Any
from PySide6.QtCore import QFile
from clickqt.core.error import ClickQtError
from click import Context
import sys
from io import StringIO, BytesIO

class FileFild(TextField):
    widget_type = QLineEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)
        self.click_object = kwargs.get("o").type
        self.click_command = kwargs.get("com")

        if options.get("type") and options["type"].get("mode") and "r" in options["type"]["mode"]:
            def onValueChanged():
                if self.widget.text() and self.widget.text() != "-" and not QFile.exists(self.widget.text()):
                    self.widget.setStyleSheet("border: 1px solid red")
                else: # Reset the border color
                    self.widget.setStyleSheet("")

            self.widget.textChanged.connect(onValueChanged)

    def browse(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        if dialog.exec():
            filenames = dialog.selectedFiles()
            if filenames and len(filenames):
                self.setValue(filenames[0])

    def getValue(self) -> Tuple[Any, ClickQtError]:
        if "r" in self._options["type"]["mode"]:
            if self.widget.text() == "-":
                old_stdin = sys.stdin
                user_input, _ = QInputDialog().getMultiLineText(self.widget, 'Stdin Input', self.label.text())
                sys.stdin = BytesIO(user_input.encode(sys.stdin.encoding)) if "b" in self._options["type"]["mode"] else StringIO(user_input)
                ret_val = (self.click_object.convert(value=self.widget.text(), param=None, ctx=Context(self.click_command)), ClickQtError.NO_ERROR)
                sys.stdin = old_stdin
                return ret_val
            elif self.widget.text() and QFile.exists(self.widget.text()):
                return (self.click_object.convert(value=self.widget.text(), param=None, ctx=Context(self.click_command)), ClickQtError.NO_ERROR)
            else:
                return (None, ClickQtError.PATH_NOT_EXIST_ERROR)
        else:
            return (self.click_object.convert(value=self.widget.text(), param=None, ctx=Context(self.click_command)), ClickQtError.NO_ERROR)
   