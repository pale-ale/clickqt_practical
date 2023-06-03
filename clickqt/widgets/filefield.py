from PySide6.QtWidgets import QLineEdit, QInputDialog
from clickqt.widgets.base_widget import PathField
from typing import Tuple, Any
from PySide6.QtCore import QFile
from clickqt.core.error import ClickQtError
from click import Context
import sys
from io import StringIO, BytesIO
import re

class FileFild(PathField):
    widget_type = QLineEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.click_object = kwargs.get("o").type
        self.click_command = kwargs.get("com")

        self.file_type = PathField.FileType.File

    def isValid(self) -> bool:
        if self.widget.text() != "-" and \
            (self.is_pseudo() or ("r" in self.options["type"]["mode"] and not QFile.exists(self.widget.text()))):
            self.handleValid(False)
            return False
        else: # Reset the border color
            self.handleValid(True)
            return True
        
    def is_pseudo(self) -> bool:
        return re.match(r"^(\.*/*)*$", self.widget.text())   

    def getValue(self) -> Tuple[Any, ClickQtError]:
        value, err = self.callback_validate()
        if err.type != ClickQtError.ErrorType.NO_ERROR:
            self.handleValid(False)
            return (value, err)

        if "r" in self.options["type"]["mode"]:
            if self.widget.text() == "-":
                def ret():
                    old_stdin = sys.stdin
                    user_input, ok = QInputDialog.getMultiLineText(self.widget, 'Stdin Input', self.label.text())
                    if not ok:
                        return (None, ClickQtError(ClickQtError.ErrorType.ABORTED_ERROR))
                    
                    sys.stdin = BytesIO(user_input.encode(sys.stdin.encoding)) if "b" in self.options["type"]["mode"] else StringIO(user_input)
                    ret_val = (self.click_object.convert(value=self.widget.text(), param=None, ctx=Context(self.click_command)), ClickQtError())
                    sys.stdin = old_stdin
                    return ret_val
                return (ret, ClickQtError())
            elif self.isValid():
                return (self.click_object.convert(value=self.widget.text(), param=None, ctx=Context(self.click_command)), ClickQtError())
            else:
                return (None, ClickQtError(ClickQtError.ErrorType.FILE_NOT_EXIST_ERROR, self.widget_name))
        elif not self.isValid():
            return (None, ClickQtError(ClickQtError.ErrorType.INVALID_FILENAME_ERROR, self.widget_name))
        else:
            return (self.click_object.convert(value=self.widget.text(), param=None, ctx=Context(self.click_command)), ClickQtError())
   
    def getWidgetValue(self) -> str:
        return self.widget.text()