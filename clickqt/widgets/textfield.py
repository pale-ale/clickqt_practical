from PySide6.QtWidgets import QLineEdit, QPushButton, QFileDialog
from PySide6.QtCore import QDir
from clickqt.widgets.core.QPathDialog import QPathDialog
from clickqt.widgets.basewidget import BaseWidget
from clickqt.core.utils import remove_prefix
from typing import Any
from enum import IntFlag
from click import Parameter, Context, ParamType
try:
    from enum_tools.documentation import document_enum
except ImportError:
    document_enum = lambda x: x

class TextField(BaseWidget):
    """Represents a click.types.StringParamType-object and user defined click types.
     
    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for 
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QLineEdit

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

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
        """Returns True if the current text is an empty string, False otherwise."""

        return self.getWidgetValue() == ""
    
    def getWidgetValue(self) -> str:
        return self.widget.text()
    

class PathField(TextField):
    """Provides basic functionalities for click.types.File- and click.types.Path-objects.
     
    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for 
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    @document_enum
    class FileType(IntFlag):
        """Specifies the possible file types."""

        Unknown = 0
        File = 1    # doc: The widget accepts files.
        Directory = 2 # doc: The widget accepts directories.

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        self.file_type:PathField.FileType = PathField.FileType.Unknown #: File type of this widget, defaults to :attr:`~clickqt.widgets.textfield.PathField.FileType.Unknown`.

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse)
        self.layout.addWidget(self.browse_btn)

    def setValue(self, value:Any):
        self.widget.setText(str(value))

    def browse(self):
        """Opens a :class:`~clickqt.widgets.core.QPathDialog.QPathDialog` if :attr:`~clickqt.widgets.textfield.PathField.file_type` is of type 
        :attr:`~clickqt.widgets.textfield.PathField.FileType.File` and :attr:`~clickqt.widgets.textfield.PathField.FileType.Directory`, a
        :class:`~PySide6.QtWidgets.QFileDialog` otherwise. Sets the relative path or absolute path (-> path does not contain the path of this project) 
        that was selected in the dialog as the value of the widget.
        """

        assert self.file_type != PathField.FileType.Unknown

        if (self.file_type & PathField.FileType.File and self.file_type & PathField.FileType.Directory):
            dialog = QPathDialog(None, directory=QDir.currentPath(), exist=self.type.exists)
            if dialog.exec():
                self.handleValid(True)
                self.setValue(remove_prefix(dialog.selectedPath().replace(QDir.currentPath(), "").replace("/", QDir.separator()), QDir.separator()))
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
                    self.setValue(remove_prefix(filenames[0].replace(QDir.currentPath(), "").replace("/", QDir.separator()), QDir.separator())) 
