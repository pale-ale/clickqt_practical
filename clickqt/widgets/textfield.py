from __future__ import annotations

from enum import IntFlag
import typing as t

import click
from PySide6.QtWidgets import QLineEdit, QPushButton, QFileDialog, QHBoxLayout, QWidget
from PySide6.QtCore import QDir

from clickqt.widgets.core.QPathDialog import QPathDialog
from clickqt.widgets.basewidget import BaseWidget
from clickqt.core.utils import remove_prefix

try:
    from enum_tools.documentation import document_enum
except ImportError:  # pragma: no cover
    document_enum = lambda x: x # pylint: disable=unnecessary-lambda-assignment


class TextField(BaseWidget):
    """Represents a click.types.StringParamType-object and user defined click types.

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QLineEdit

    def __init__(self, otype: click.ParamType, param: click.Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        if self.parent_widget is None:
            if (
                envvar_value := param.resolve_envvar_value(click.Context(self.click_command))
            ) is not None:  # Consider envvar
                self.set_value(envvar_value)
            else:  # Consider default value
                self.set_value(BaseWidget.get_param_default(param, ""))

    def set_value(self, value: t.Any):
        if isinstance(value, str):
            self.widget.setText(value)
        else:
            self.widget.setText(
                self.type.convert(
                    value=value,
                    param=self.click_command,
                    ctx=click.Context(self.click_command),
                )
            )

    def is_empty(self) -> bool:
        """Returns True if the current text is an empty string, False otherwise."""

        return self.get_widget_value() == ""

    def get_widget_value(self) -> str:
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
        File = 1  # doc: The widget accepts files.
        Directory = 2  # doc: The widget accepts directories.

    def __init__(self, otype: click.ParamType, param: click.Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        self.file_type: PathField.FileType = (
            PathField.FileType.Unknown
        )  #: File type of this widget, defaults to :attr:`~clickqt.widgets.textfield.PathField.FileType.Unknown`.

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse)
        self.layout.removeWidget(self.widget)
        input_btn_container = QWidget()
        input_btn_container.setLayout(QHBoxLayout())
        input_btn_container.layout().setContentsMargins(0, 0, 0, 0)
        input_btn_container.layout().addWidget(self.widget)
        input_btn_container.layout().addWidget(self.browse_btn)
        self.layout.addWidget(input_btn_container)

    def set_value(self, value: t.Any):
        self.widget.setText(str(value))

    def browse(self):
        """Opens a :class:`~clickqt.widgets.core.QPathDialog.QPathDialog` if :attr:`~clickqt.widgets.textfield.PathField.file_type` is of type
        :attr:`~clickqt.widgets.textfield.PathField.FileType.File` and :attr:`~clickqt.widgets.textfield.PathField.FileType.Directory`, a
        :class:`~PySide6.QtWidgets.QFileDialog` otherwise. Sets the relative path or absolute path (-> path does not contain the path of this project)
        that was selected in the dialog as the value of the widget.
        """

        assert self.file_type != PathField.FileType.Unknown

        if (
            self.file_type & PathField.FileType.File
            and self.file_type & PathField.FileType.Directory
        ):
            dialog = QPathDialog(
                None, directory=QDir.currentPath(), exist=self.type.exists
            )
            if dialog.exec():
                self.handle_valid(True)
                self.set_value(
                    remove_prefix(
                        dialog.selectedPath()
                        .replace(QDir.currentPath(), "")
                        .replace("/", QDir.separator()),
                        QDir.separator(),
                    )
                )
        else:
            dialog = QFileDialog(directory=QDir.currentPath())
            dialog.setViewMode(QFileDialog.ViewMode.Detail)
            dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
            # File or directory selectable
            if self.file_type == PathField.FileType.File:
                # click.File hasn't "exists" attribute, click.Path hasn't "mode" attribute
                if (hasattr(self.type, "exists") and self.type.exists) or (
                    hasattr(self.type, "mode") and "r" in self.type.mode
                ):
                    dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
                else:
                    dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            else:  # Only FilePathField can be here
                dialog.setFileMode(QFileDialog.FileMode.Directory)
                dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

            if dialog.exec():
                filenames = dialog.selectedFiles()
                if filenames and len(filenames) > 0:
                    self.handle_valid(True)
                    self.set_value(
                        remove_prefix(
                            filenames[0]
                            .replace(QDir.currentPath(), "")
                            .replace("/", QDir.separator()),
                            QDir.separator(),
                        )
                    )
