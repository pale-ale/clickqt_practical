from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import QFile
from clickqt.widgets.filefield import FileFild
from typing import Tuple
from clickqt.core.error import ClickQtError

class PathField(FileFild):
    widget_type = QLineEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        def onValueChanged():
            if options.get("type").get("exists") and self.widget.text() and not QFile.exists(self.widget.text()):
                self.widget.setStyleSheet("border: 1px solid red")
            else: # Reset the border color
                self.widget.setStyleSheet("")

        self.widget.textChanged.connect(onValueChanged)


    def getValue(self) -> Tuple[str, ClickQtError]:
        return self.widget.text(), ClickQtError.PATH_NOT_EXIST_ERROR if self._options.get("type").get("exists") and not QFile.exists(self.widget.text()) \
                                    else ClickQtError.NO_ERROR
   