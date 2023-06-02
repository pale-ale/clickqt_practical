from typing import Any, Tuple
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QFileDialog
from PySide6.QtCore import QDir
from clickqt.core.error import ClickQtError
from clickqt.widgets.core.QPathDialog import QPathDialog
from enum import IntFlag

class BaseWidget(ABC):
    # The type of this widget
    widget_type: Any

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.widget_name = options.get('name', 'Unknown')
        self.container = QWidget()
        self.layout = QHBoxLayout()
        self.label = QLabel(text=f"{kwargs.get('label', '')}{self.widget_name}: ")
        self.label.setToolTip(options.get("help", "No options available"))
        self.widget = self.createWidget(args, kwargs)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.widget)
        self.container.setLayout(self.layout)

    def createWidget(self, *args, **kwargs):
        return self.widget_type()

    @abstractmethod
    def setValue(self, value):
        pass

    @abstractmethod
    def getValue(self) -> Tuple[Any, ClickQtError]:
        pass


class NumericField(BaseWidget):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.setValue(options.get("default")() if callable(options.get("default")) \
                else options.get("default") or 0)

    def setValue(self, value: int|float):
        self.widget.setValue(value)

    def setMinimum(self, value: int|float):
        self.widget.setMinimum(value)

    def setMaximum(self, value: int|float):
         self.widget.setMaximum(value)

    def getMinimum(self) -> int|float:
        self.widget.minimum()

    def getMaximum(self) -> int|float:
        self.widget.maximum()

    def getValue(self) -> Tuple[int|float, ClickQtError]:
        return self.widget.value(), ClickQtError()


class ComboBoxBase(BaseWidget):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.addItems(options.get("type").get("choices"))
        
    def setValue(self, value: str):
        self.widget.setCurrentText(value)

    @abstractmethod
    def addItems(self, items):
        pass


class PathField(BaseWidget):
    class FileType(IntFlag):
        Unknown = 0
        File = 1
        Directory = 2

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.setValue(options.get("default")() if callable(options.get("default")) \
                else options.get("default") or "")
        
        self.file_type = PathField.FileType.Unknown

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)

        self.widget.textChanged.connect(self.isValid)

    @abstractmethod
    def isValid(self) -> bool:
        pass

    def setValue(self, value: str):
        self.widget.setText(value)

    def browse(self):
        """
            Sets the relative path or absolute path (when the path does not contain the path of this project) in the textfield
        """
        assert(self.file_type != PathField.FileType.Unknown)

        if self.file_type & PathField.FileType.File and self.file_type & PathField.FileType.Directory:
            dialog = QPathDialog(None, self.options["type"]["exists"])
            if dialog.exec():
                self.setValue(dialog.selectedPath().replace(QDir.currentPath(), "").replace("/", QDir.separator()).removeprefix(QDir.separator()))
        else:
            dialog = QFileDialog()
            dialog.setViewMode(QFileDialog.ViewMode.Detail)
            dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
            # File or directory selectable
            if self.file_type == PathField.FileType.File:
                # click.File hasn't "exists" attribute, click.Path hasn't "mode" attribute
                if self.options["type"].get("exists", False) or "r" in self.options["type"].get("mode", ""):
                    dialog.setFileMode(QFileDialog.FileMode.ExistingFile) 
                else:
                    dialog.setFileMode(QFileDialog.FileMode.AnyFile)  
            else: # Only FilePathField can be here
                if self.options["type"]["exists"]:
                    dialog.setFileMode(QFileDialog.FileMode.Directory)
                else:
                    dialog.setFileMode(QFileDialog.FileMode.AnyFile)
                
                dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
            
            if dialog.exec():
                filenames = dialog.selectedFiles()
                if filenames and len(filenames):
                    self.setValue(filenames[0].replace(QDir.currentPath(), "").replace("/", QDir.separator()).removeprefix(QDir.separator())) 
    