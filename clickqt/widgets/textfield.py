from PySide6.QtWidgets import QLineEdit, QPushButton, QFileDialog
from PySide6.QtCore import QDir
from clickqt.widgets.core.QPathDialog import QPathDialog
from clickqt.widgets.base_widget import BaseWidget
from enum import IntFlag
from click import Parameter, Option

class TextField(BaseWidget):
    widget_type = QLineEdit

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)
        self.setValue(BaseWidget.getParamDefault(param, ""))

    def setValue(self, value: str):
        if isinstance(value, str):
            self.widget.setText(value)

    def isEmpty(self) -> bool:
        return self.getWidgetValue() == ""
    
    def getWidgetValue(self) -> str:
        return self.widget.text()
    

class PathField(TextField):
    class FileType(IntFlag):
        Unknown = 0
        File = 1
        Directory = 2

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)
        self.setValue(BaseWidget.getParamDefault(param, ""))
        
        self.file_type = PathField.FileType.Unknown

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)

    def browse(self):
        """
            Sets the relative path or absolute path (when the path does not contain the path of this project) in the textfield
        """
        assert self.file_type != PathField.FileType.Unknown

        if self.file_type & PathField.FileType.File and self.file_type & PathField.FileType.Directory:
            dialog = QPathDialog(None, self.param.type.exists)
            if dialog.exec():
                self.handleValid(True)
                self.setValue(dialog.selectedPath().replace(QDir.currentPath(), "").replace("/", QDir.separator()).removeprefix(QDir.separator()))
        else:
            dialog = QFileDialog()
            dialog.setViewMode(QFileDialog.ViewMode.Detail)
            dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
            # File or directory selectable
            if self.file_type == PathField.FileType.File:
                # click.File hasn't "exists" attribute, click.Path hasn't "mode" attribute
                if (hasattr(self.param.type, "exists") and self.param.type.exists) or \
                    (hasattr(self.param.type, "mode") and "r" in self.param.type.mode):
                    dialog.setFileMode(QFileDialog.FileMode.ExistingFile) 
                else:
                    dialog.setFileMode(QFileDialog.FileMode.AnyFile)  
            else: # Only FilePathField can be here
                if self.param.type.exists:
                    dialog.setFileMode(QFileDialog.FileMode.Directory)
                else:
                    dialog.setFileMode(QFileDialog.FileMode.AnyFile)
                
                dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
            
            if dialog.exec():
                filenames = dialog.selectedFiles()
                if filenames and len(filenames):
                    self.handleValid(True)
                    self.setValue(filenames[0].replace(QDir.currentPath(), "").replace("/", QDir.separator()).removeprefix(QDir.separator())) 