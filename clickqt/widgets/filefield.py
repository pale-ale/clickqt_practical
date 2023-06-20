from PySide6.QtWidgets import QLineEdit, QInputDialog
from clickqt.widgets.textfield import PathField
from typing import Tuple, Any
from clickqt.core.error import ClickQtError
from click import Parameter
import sys
from io import StringIO, BytesIO

class FileFild(PathField):
    widget_type = QLineEdit

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)

        self.file_type = PathField.FileType.File

    def getValue(self) -> Tuple[Any, ClickQtError]:
        if "r" in self.param.type.mode and self.widget.text() == "-":
            self.handleValid(True)

            def ret():
                user_input, ok = QInputDialog.getMultiLineText(self.widget, 'Stdin Input', self.label.text())
                if not ok:
                    return (None, ClickQtError(ClickQtError.ErrorType.ABORTED_ERROR))
                
                old_stdin = sys.stdin
                sys.stdin = BytesIO(user_input.encode(sys.stdin.encoding)) if "b" in self.param.type.mode else StringIO(user_input)
                val = super(FileFild, self).getValue()
                sys.stdin = old_stdin
                return val
            
            return (ret, ClickQtError())
        else:
            return super().getValue()
