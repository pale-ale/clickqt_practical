from PySide6.QtWidgets import QLineEdit, QInputDialog
from clickqt.widgets.textfield import PathField
from typing import Tuple, Any
from clickqt.core.error import ClickQtError
from click import Parameter, ParamType, File
import sys
from io import StringIO, BytesIO

class FileField(PathField):
    """Represents a click.types.File object.
    
    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for 
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QLineEdit #: The Qt-type of this widget.

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert isinstance(otype, File), f"'otype' must be of type '{File}', but is '{type(otype)}'."

        self.file_type:PathField.FileType = PathField.FileType.File #: File type is a :attr:`~clickqt.widgets.textfield.PathField.FileType.File`.

    def getValue(self) -> Tuple[Any, ClickQtError]:
        """Opens a input dialog that represents sys.stdin if 'r' is in **otype**\.mode and the current widget value '-' is, passes the input to 
        :func:`~clickqt.widgets.basewidget.BaseWidget.getValue` and returns the result.

        :return: Valid: (widget value or the value of a callback, :class:`~clickqt.core.error.ClickQtError.ErrorType.NO_ERROR`)\n
                 Invalid: (None, :class:`~clickqt.core.error.ClickQtError.ErrorType.CONVERTING_ERROR` or 
                 :class:`~clickqt.core.error.ClickQtError.ErrorType.PROCESSING_VALUE_ERROR` or :class:`~clickqt.core.error.ClickQtError.ErrorType.ABORTED_ERROR`)
        """

        if "r" in self.type.mode and self.widget.text() == "-":
            self.handleValid(True)

            def ret(): # FocusOutValidator should not open this dialog
                user_input, ok = QInputDialog.getMultiLineText(self.widget, 'Stdin Input', self.label.text())
                if not ok:
                    return (None, ClickQtError(ClickQtError.ErrorType.ABORTED_ERROR))
                
                old_stdin = sys.stdin
                sys.stdin = BytesIO(user_input.encode(sys.stdin.encoding)) if "b" in self.type.mode else StringIO(user_input)
                val = super(FileField, self).getValue()
                sys.stdin = old_stdin
                return val

            return (ret, ClickQtError())
        else:
            return super().getValue()
