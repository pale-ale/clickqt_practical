from typing import Any, Tuple
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QFileDialog
from PySide6.QtCore import QDir
from clickqt.core.error import ClickQtError
from clickqt.widgets.core.QPathDialog import QPathDialog
from clickqt.core.callbackvalidator import CallbackValidator
from enum import IntFlag
from click import Context, Parameter

class BaseWidget(ABC):
    # The type of this widget
    widget_type: Any

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.click_object: Parameter = kwargs.get("o")
        self.click_command = kwargs.get("com")
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
        assert self.click_object is not None, "Click object not provided"
        assert self.click_command is not None, "Click command not provided"
        
        if self.click_object.callback:
            self.callback_validator = CallbackValidator(self)
            self.widget.installEventFilter(self.callback_validator)
    
    def createWidget(self, *args, **kwargs):
        return self.widget_type()

    @abstractmethod
    def setValue(self, value):
        """
            Sets the value of the widget
        """
        pass

    def getValue(self) -> Tuple[Any, ClickQtError]:
        """
            Validates the value of the widget and returns the result\n
            Valid -> (widget value or the value of a callback, ClickQtError.ErrorType.NO_ERROR)\n
            Invalid -> (None, CClickQtError.ErrorType.CONVERTION_ERROR or ClickQtError.ErrorType.CALLBACK_VALIDATION_ERROR)
        """
        value: Any = None

        try: # Try to convert the provided value into the corresponding click object type
            if hasattr(self.click_object, "multiple") and self.click_object.multiple:
                value = []
                #TODO
                #assert not isinstance(self.getWidgetValue(), str), "There is a bug"
                for v in self.getWidgetValue():
                    value.append(self.click_object.type.convert(value=v, param=None, ctx=Context(self.click_command))) 
            else:
                value = self.click_object.type.convert(value=self.getWidgetValue(), param=None, ctx=Context(self.click_command))
        except AssertionError as e:
            raise 
        except Exception as e:
            self.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.CONVERTION_ERROR, self.widget_name, e))
            
        try: # Consider callbacks 
            value = self.click_object.process_value(Context(self.click_command), value)
        except Exception as e:
            self.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.CALLBACK_VALIDATION_ERROR, self.widget_name, e))

        self.handleValid(True)
        return (value, ClickQtError())

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
    