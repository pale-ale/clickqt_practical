from PySide6.QtWidgets import QLineEdit, QPushButton, QFileDialog
from PySide6.QtCore import QFile
from clickqt.widgets.textfield import TextField
from typing import Tuple
from clickqt.core.error import ClickQtError

class PathField(TextField):
    widget_type = QLineEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)
        
        def onValueChanged():
            if options.get("type").get("exists") and self.widget.text() and not QFile.exists(self.widget.text()):
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


    def getValue(self) -> Tuple[str, ClickQtError]:
        return self.widget.text(), ClickQtError.PATH_NOT_EXIST_ERROR if self._options.get("type").get("exists") and not QFile.exists(self.widget.text()) \
                                    else ClickQtError.NO_ERROR
   