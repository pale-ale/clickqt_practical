from PySide6.QtWidgets import QLineEdit, QPushButton, QFileDialog
from PySide6.QtCore import QDir
from clickqt.widgets.core.QPathDialog import QPathDialog
from clickqt.widgets.basewidget import BaseWidget
from typing import Any
from enum import IntFlag
from click import Parameter, Context, ParamType

class TextField(BaseWidget):
    widget_type = QLineEdit

    def __init__(self, otype:ParamType, param:Parameter, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        if self.parent_widget is None:
            if (envvar_value := param.resolve_envvar_value(Context(self.click_command))) is not None: # Consider envvar
                self.setValue(envvar_value)
            else: # Consider default value
                self.setValue(BaseWidget.getParamDefault(param, ""))

    def setValue(self, value:Any):
        if isinstance(value, str):
            self.widget.setText(value)
        else:
            self.widget.setText(self.type.convert(value=value, param=self.click_command, ctx=Context(self.click_command)))

    def isEmpty(self) -> bool:
        return self.getWidgetValue() == ""
    
    def getWidgetValue(self) -> str:
        return self.widget.text()
    

class PathField(TextField):
    class FileType(IntFlag):
        Unknown = 0
        File = 1
        Directory = 2

    def __init__(self, otype:ParamType, param:Parameter, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        self.file_type = PathField.FileType.Unknown

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)

    def setValue(self, value:Any):
        self.widget.setText(str(value))

    def browse(self):
        """
            Sets the relative path or absolute path (when the path does not contain the path of this project) in the textfield
        """
        assert self.file_type != PathField.FileType.Unknown

        if (self.file_type & PathField.FileType.File and self.file_type & PathField.FileType.Directory):
            dialog = QPathDialog(None, directory=QDir.currentPath(), exist=self.type.exists)
            if dialog.exec():
                self.handleValid(True)
                self.setValue(dialog.selectedPath().replace(QDir.currentPath(), "").replace("/", QDir.separator()).removeprefix(QDir.separator()))
        else:
            dialog = QFileDialog(directory=QDir.currentPath())
            dialog.setViewMode(QFileDialog.ViewMode.Detail)
            dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
            # File or directory selectable
            if self.file_type == PathField.FileType.File:
                # click.File hasn't "exists" attribute, click.Path hasn't "mode" attribute
                if (hasattr(self.type, "exists") and self.type.exists) or \
                    (hasattr(self.type, "mode") and "r" in self.type.mode):
                    dialog.setFileMode(QFileDialog.FileMode.ExistingFile) 
                else:
                    dialog.setFileMode(QFileDialog.FileMode.AnyFile)  
            else: # Only FilePathField can be here
                
                if self.type.exists:
                    dialog.setFileMode(QFileDialog.FileMode.Directory)
                else:
                    dialog.setFileMode(QFileDialog.FileMode.AnyFile)  

                dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
            
            if dialog.exec():
                filenames = dialog.selectedFiles()
                if filenames and len(filenames):
                    self.handleValid(True)
                    self.setValue(filenames[0].replace(QDir.currentPath(), "").replace("/", QDir.separator()).removeprefix(QDir.separator())) 
