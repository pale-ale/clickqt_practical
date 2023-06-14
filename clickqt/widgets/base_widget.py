from typing import Any
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QFileDialog
from PySide6.QtCore import QDir
from clickqt.core.error import ClickQtError
from clickqt.widgets.core.QPathDialog import QPathDialog
import clickqt.core
from enum import IntFlag
from click import Context, Parameter, Choice, Option, Tuple as click_type_tuple, Command

class BaseWidget(ABC):
    # The type of this widget
    widget_type: Any

    def __init__(self, param:Parameter, *args, parent:"BaseWidget|None"=None, **kwargs):
        assert isinstance(param, Parameter)
        self.parent_widget = parent
        self.param = param
        self.click_command = kwargs.get("com")
        self.widget_name = param.name
        self.container = QWidget()
        self.layout = QHBoxLayout()
        self.label = QLabel(text=f"{kwargs.get('label', '')}{self.widget_name}: ")
        if isinstance(param, Option):
            self.label.setToolTip(param.help)
        self.widget = self.createWidget(args, kwargs)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.widget)
        self.container.setLayout(self.layout)

        assert self.widget is not None, "Widget not initialized"
        assert self.param is not None, "Click param object not provided"
        assert self.click_command is not None, "Click command not provided"

        self.focus_out_validator = clickqt.core.FocusOutValidator(self)
        self.widget.installEventFilter(self.focus_out_validator)
    
    def createWidget(self, *args, **kwargs) -> QWidget:
        return self.widget_type()

    @abstractmethod
    def setValue(self, value):
        """
            Sets the value of the widget
        """
        pass

    def isEmpty(self) -> bool:
        """
            Checks, if the widget is empty. 
            This could happen only for string-based widgets or the multiple choice-widget
            -> Subclasses may need to override this method
        """
        return False

    def getValue(self) -> tuple[Any, ClickQtError]:
        """
            Validates the value of the widget and returns the result\n
            Valid -> (widget value or the value of a callback, ClickQtError.ErrorType.NO_ERROR)\n
            Invalid -> (None, CClickQtError.ErrorType.CONVERTING_ERROR or ClickQtError.ErrorType.PROCESSING_VALUE_ERROR)
        """
        value: Any = None

        try: # Try to convert the provided value into the corresponding click object type
            # if statement is obtained by creating the corresponding truth table
            if self.param.multiple or \
            (not isinstance(self.param.type, click_type_tuple) and self.param.nargs != 1):
                value = []
                for v in self.getWidgetValue():
                    if BaseWidget.isRequiredValidInput(self.param, v):
                        self.handleValid(False)
                        return (None, ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR, self.widget_name, self.param.param_type_name))

                    value.append(self.param.type.convert(value=v, param=self.param, ctx=Context(self.click_command))) 
            else:
                if BaseWidget.isRequiredValidInput(self.param, self):
                    self.handleValid(False)
                    return (None, ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR, self.widget_name, self.param.param_type_name))
                
                value = self.param.type.convert(value=self.getWidgetValue(), param=self.param, ctx=Context(self.click_command))
        except Exception as e:
            self.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.CONVERTING_ERROR, self.widget_name, e))
        
        try: # Consider callbacks 
            ret_val = (self.param.process_value(Context(self.click_command), value), ClickQtError())
            self.handleValid(True)
            return ret_val
        except Exception as e:
            self.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.PROCESSING_VALUE_ERROR, self.widget_name, e))

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
    
    @staticmethod
    def getParamDefault(param:Parameter, alternative=None):
        if param.default is None:
            return alternative
        if callable(param.default):
            return param.default()
        return param.default
    
    @staticmethod
    def isRequiredValidInput(param:Parameter, widget:"BaseWidget"):
        # If there is a default, click will use this (-> required option/argument can be omitted)
        return param.required and widget.isEmpty() and BaseWidget.getParamDefault(param, None) is None


class NumericField(BaseWidget):
    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)
        self.setValue(BaseWidget.getParamDefault(param, 0))

    def setValue(self, value: int|float):
        if isinstance(value, int|float):
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
    def __init__(self, param:Parameter, *args, **kwargs):
        if not isinstance(param.type, Choice):
            raise TypeError(f"'param' must be of type 'Choice'.")
        super().__init__(param, *args, **kwargs)
        self.addItems(param.type.choices)

    def setValue(self, value: str):
        if isinstance(value, str):
            self.widget.setCurrentText(value)

    # Changing the border color does not work because overwriting 
    # the default stylesheet settings results in a program crash (TODO)
    def handleValid(self, valid: bool):
        pass

    @abstractmethod
    def addItems(self, items):
        pass


class PathField(BaseWidget):
    class FileType(IntFlag):
        Unknown = 0
        File = 1
        Directory = 2

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)

        if isinstance(param, Option):
            self.setValue(BaseWidget.getParamDefault(param, ""))
        
        self.file_type = PathField.FileType.Unknown

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)

    def setValue(self, value: str):
        if isinstance(value, str):
            self.widget.setText(value)

    #def isEmpty(self) -> bool:
    #    return False # click rejects empty paths/filenames

    def browse(self):
        """
            Sets the relative path or absolute path (when the path does not contain the path of this project) in the textfield
        """
        assert(self.file_type != PathField.FileType.Unknown)

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
    