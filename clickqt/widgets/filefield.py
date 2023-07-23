""" Contains the FileField class """
from __future__ import annotations

import sys
from io import StringIO, BytesIO
import typing as t

import click
from PySide6.QtWidgets import QLineEdit, QInputDialog

from clickqt.core.error import ClickQtError
from clickqt.widgets.textfield import PathField


class FileField(PathField):
    """Represents a click.types.File object.

    :param otype: The type which specifies the clickqt widget type.
        This type may differ from **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additional parameters ('parent', 'widgetsource', 'com', 'label') needed for
        :class:`~clickqt.widgets.basewidget.MultiWidget`- /
        :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`- widgets
    """

    widget_type = QLineEdit  #: The Qt-type of this widget.

    def __init__(self, otype: click.ParamType, param: click.Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert isinstance(
            otype, click.File
        ), f"'otype' must be of type '{click.File}', but is '{type(otype)}'."

        self.file_type: PathField.FileType = (
            PathField.FileType.File
        )  #: File type is a :attr:`~clickqt.widgets.textfield.PathField.FileType.File`.

    def get_value(self) -> tuple[t.Any, ClickQtError]:
        """
        Opens an input dialogue that represents sys.stdin if 'r' is in **otype**.mode
            and the current widget value is '-', passes the input to
        :func:`~clickqt.widgets.basewidget.BaseWidget.get_value`, and returns the result.

        :return:
            Valid: (widget value or the value of a callback,
                :class:`~clickqt.core.error.ClickQtError.ErrorType.NO_ERROR`)\n
            Invalid: (None, :class:`~clickqt.core.error.ClickQtError.ErrorType.CONVERTING_ERROR` or
                :class:`~clickqt.core.error.ClickQtError.ErrorType.PROCESSING_VALUE_ERROR` or
                :class:`~clickqt.core.error.ClickQtError.ErrorType.ABORTED_ERROR`)
        """

        if "r" in self.type.mode and self.widget.text() == "-":
            self.handle_valid(True)

            def ret():  # FocusOutValidator should not open this dialog
                user_input, is_ok = QInputDialog.getMultiLineText(
                    self.widget, "Stdin Input", self.label.text()
                )
                if not is_ok:
                    return (None, ClickQtError(ClickQtError.ErrorType.ABORTED_ERROR))

                old_stdin = sys.stdin
                sys.stdin = (
                    BytesIO(user_input.encode(sys.stdin.encoding))
                    if "b" in self.type.mode
                    else StringIO(user_input)
                )
                val = super(  # pylint: disable=super-with-arguments
                    FileField, self
                ).get_value()
                sys.stdin = old_stdin
                return val

            return (ret, ClickQtError())
        return super().get_value()
