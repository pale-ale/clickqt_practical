from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import QFile
from clickqt.widgets.base_widget import PathField
from typing import Tuple
from clickqt.core.error import ClickQtError

class FilePathField(PathField):
    widget_type = QLineEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.file_type |= PathField.FileType.File if options["type"]["file_okay"] else self.file_type
        self.file_type |= PathField.FileType.Directory if options["type"]["dir_okay"] else self.file_type

        if self.file_type == PathField.FileType.Unknown:
            raise ValueError(f"Neither 'file_okay' nor 'dir_okay' in argument '{self.widget_name}' is set")
    
    def isValid(self) -> bool:
        if self.options["type"]["exists"] and not QFile.exists(self.widget.text()):
            self.widget.setStyleSheet("border: 1px solid red")
            return False
        else: # Reset the border color
            self.widget.setStyleSheet("")
            return True

    def getValue(self) -> Tuple[str, ClickQtError]:
        if not self.isValid():
            return ("", ClickQtError(ClickQtError.ErrorType.PATH_NOT_EXIST_ERROR, self.widget_name))
        else:
            return (self.widget.text(), ClickQtError())
   