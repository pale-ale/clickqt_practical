from typing import Any, Tuple
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QFileDialog
from PySide6.QtCore import QDir
from clickqt.core.error import ClickQtError
from clickqt.widgets.core.QPathDialog import QPathDialog
from clickqt.core.callbackvalidator import CallbackValidator
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
        self.callback_validator: CallbackValidator = None

        assert self.widget is not None, "Widget not initialized"
        
        if kwargs["o"].callback:
            self.callback_validator = CallbackValidator(kwargs["com"], kwargs["o"], self)
            self.widget.installEventFilter(self.callback_validator)
    
    def createWidget(self, *args, **kwargs):
        return self.widget_type()

    @abstractmethod
    def setValue(self, value):
        """
            Sets the value of the widget
        """
        pass

    @abstractmethod
    def getValue(self) -> Tuple[Any, ClickQtError]:
        """
            Validates the value of the widget and returns the result\n
            Valid -> (widget_value, ClickQtError.ErrorType.NO_ERROR)\n
            Invalid -> (None or zero initialized type, Any ClickQtError error)
        """
        pass

    @abstractmethod
    def getWidgetValue(self) -> Any:
        """
            Returns the value of the widget without any checks
        """
        pass

    def handleValid(self, valid: bool):
        if not valid:
            self.widget.setStyleSheet("border: 1px solid red")
        else:
            self.widget.setStyleSheet("")

    def callback_validate(self) -> Tuple[Any, ClickQtError]:
        if self.callback_validator:
            value, err = self.callback_validator.validate()
            if err.type != ClickQtError.ErrorType.NO_ERROR:
                return (value, err)
            
        return (None, ClickQtError())


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
        value, err = self.callback_validate()
        if err.type != ClickQtError.ErrorType.NO_ERROR:
            self.handleValid(False)
            return (value, err)
        
        return (self.getWidgetValue(), ClickQtError())
    
    def getWidgetValue(self) -> int|float:
        return self.widget.value()

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
    