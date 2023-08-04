from typing import Type, Optional, Any
import click
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QCheckBox,
    QDateTimeEdit,
    QSpinBox,
)
from PySide6.QtCore import Qt
from clickqt.core.error import ClickQtError
import clickqt.core as clickqt_core


class WidgetNotSupported(Exception):
    """Exception stating that the a widget is not supported by clickqt yet for user defined click types."""

    def __init__(self, widget_name):
        super().__init__(f"{widget_name} not supported.")
        self.widget_name = widget_name


class CustomWidget:
    """CustomWidget class used for the creation of widgets of user defined click types by the
    wish of the user.
    :param widget_class: The kind of widget the user wants to map his user defined click type.
    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param parent: The parent BaseWidget of **otype**, defaults to None. Needed for :class:`~clickqt.widgets.basewidget.MultiWidget`-widgets
    :param kwargs: Additionally parameters ('widgetsource', 'com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    def __init__(
        self,
        widget_class: Type[QWidget],
        otype: click.ParamType,
        param: click.Parameter,
        parent: Optional["CustomWidget"] = None,
        **kwargs,
    ):
        assert issubclass(
            widget_class, QWidget
        )  # Check if widget_class is a QWidget subclass
        self.widget_type = widget_class
        self.type = otype
        self.param = param
        self.parent_widget = parent
        self.click_command: click.Command = kwargs.get("com")
        self.widget_name = param.name
        self.container = QWidget()
        self.layout = (
            QVBoxLayout()
            if parent is None or kwargs.get("vboxlayout")
            else QHBoxLayout()
        )
        self.label = QLabel(text=f"<b>{kwargs.get('label', '')}{self.widget_name}</b>")
        self.label.setTextFormat(Qt.TextFormat.RichText)  # Bold text

        self.widget = self.create_widget()
        self.layout.addWidget(self.label)
        if (
            isinstance(param, click.Option)
            and param.help
            and (parent is None or kwargs.get("vboxlayout"))
        ):  # Help text
            help_label = QLabel(text=param.help)
            help_label.setWordWrap(True)  # Multi-line
            self.layout.addWidget(help_label)
        self.layout.addWidget(self.widget)
        self.container.setLayout(self.layout)

        self.widget.setObjectName(param.name)
        assert self.widget is not None, "Widget not initialized"
        assert self.param is not None, "Click param object not provided"
        assert self.click_command is not None, "Click command not provided"
        assert self.type is not None, "Type not provided"

        self.focus_out_validator = clickqt_core.FocusOutValidator(self)
        self.widget.installEventFilter(self.focus_out_validator)
        self.supported_widgets = {
            QLineEdit: {
                "setter": self.widget.setText
                if hasattr(self.widget, "setText")
                else None,
                "getter": self.widget.text if hasattr(self.widget, "text") else None,
            },
            QDateTimeEdit: {
                "setter": self.widget.setDateTime
                if hasattr(self.widget, "setDateTime")
                else None,
                "getter": self.widget.dateTime
                if hasattr(self.widget, "dateTime")
                else None,
            },
            QCheckBox: {
                "setter": self.widget.setChecked
                if hasattr(self.widget, "setChecked")
                else None,
                "getter": self.widget.isChecked
                if hasattr(self.widget, "isChecked")
                else None,
            },
            QSpinBox: {
                "setter": self.widget.setValue
                if hasattr(self.widget, "setValue")
                else None,
                "getter": self.widget.value if hasattr(self.widget, "value") else None,
            },
        }

    def create_widget(self) -> QWidget:
        """Creates the widget specified in widget_type and returns it."""
        return self.widget_type()

    def set_value(self, value: Any):
        """Sets the value of the Qt-widget based on the provided value."""
        # Implement the logic to set the value of the widget of type self.widget_type
        # based on the provided value.
        try:
            setter_function = self.supported_widgets[self.widget_type]["setter"]
            setter_function(value)
        except WidgetNotSupported as w:
            raise WidgetNotSupported(
                f"{self.widget_type.__name__} not supported."
            ) from w

    def get_widget_value(self):
        """Returns the value of the Qt-widget without any checks."""
        # Implement the logic to get the value of the widget of type self.widget_type
        # and return it.
        try:
            getter_function = self.supported_widgets[self.widget_type]["getter"]
            return getter_function()
        except WidgetNotSupported as w:
            raise WidgetNotSupported(
                f"{self.widget_type.__name__} not supported."
            ) from w

    def is_empty(self) -> bool:
        return False

    def handle_valid(self, valid: bool):
        """Changes the border of the widget dependent on **valid**. If **valid** == False, the border will be colored red, otherwise black.

        :param valid: Specifies whether there was no error when validating the widget

        """

        if not valid:
            self.widget.setStyleSheet(
                f"QWidget#{self.widget.objectName()}{{ border: 1px solid red }}"
            )
        else:
            self.widget.setStyleSheet(f"QWidget#{self.widget.objectName()}{{ }}")

    def get_value(self) -> tuple[Any, ClickQtError]:
        """Validates the value of the Qt-widget and returns the result.

        :return: Valid: (widget value or the value of a callback, :class:`~clickqt.core.error.ClickQtError.ErrorType.NO_ERROR`)\n
                 Invalid: (None, :class:`~clickqt.core.error.ClickQtError.ErrorType.CONVERTING_ERROR` or
                 :class:`~clickqt.core.error.ClickQtError.ErrorType.PROCESSING_VALUE_ERROR` or :class:`~clickqt.core.error.ClickQtError.ErrorType.REQUIRED_ERROR`)
        """
        value: Any = None

        # Try to convert the provided value into the corresponding click object type
        try:
            default = CustomWidget.get_param_default(self.param, None)

            # Check if the widget value is missing (empty)
            value_missing = False
            widget_value = self.get_widget_value()

            # Handle single value
            if self.is_empty():
                if self.param.required and default is None:
                    self.handle_valid(False)
                    return (
                        None,
                        clickqt_core.ClickQtError(
                            clickqt_core.ClickQtError.ErrorType.REQUIRED_ERROR,
                            self.widget_name,
                            self.param.param_type_name,
                        ),
                    )
                # Set the default value if available and the widget is empty
                if default is not None:
                    self.set_value(default)
                else:
                    value_missing = True  # -> value is None
            # If no value is missing, convert the widget value
            if not value_missing:
                value = self.type.convert(
                    value=widget_value,
                    param=self.param,
                    ctx=click.Context(self.click_command),
                )

        except Exception as e:
            self.handle_valid(False)
            return (
                None,
                ClickQtError(
                    ClickQtError.ErrorType.CONVERTING_ERROR, self.widget_name, e
                ),
            )

        return self.handle_callback(value)

    def handle_callback(self, value: Any) -> tuple[Any, ClickQtError]:
        """Validates **value** in the user-defined callback (if provided) and returns the result.

        :param value: The value that should be validated in the callback

        :return: Valid: (**value** or the value of a callback, :class:`~clickqt.core.error.ClickQtError.ErrorType.NO_ERROR`)\n
                 Invalid: (None, :class:`~clickqt.core.error.ClickQtError.ErrorType.ABORTED_ERROR` or
                 :class:`~clickqt.core.error.ClickQtError.ErrorType.EXIT_ERROR` or :class:`~clickqt.core.error.ClickQtError.ErrorType.PROCESSING_VALUE_ERROR`)
        """

        try:  # Consider callbacks
            ret_val = (
                self.param.process_value(click.Context(self.click_command), value),
                ClickQtError(),
            )
            self.handle_valid(True)
            return ret_val
        except click.exceptions.Abort:
            return (None, ClickQtError(ClickQtError.ErrorType.ABORTED_ERROR))
        except click.exceptions.Exit:
            return (None, ClickQtError(ClickQtError.ErrorType.EXIT_ERROR))
        except Exception as e:
            self.handle_valid(False)
            return (
                None,
                ClickQtError(
                    ClickQtError.ErrorType.PROCESSING_VALUE_ERROR, self.widget_name, e
                ),
            )

    @staticmethod
    def get_param_default(param: click.Parameter, alternative: Any = None):
        """Returns the default value of **param**. If there is no default value, **alternative** will be returned."""

        # TODO: Replace with param.get_default(ctx=click.Context(command), call=True)
        if param.default is None:
            return alternative
        if callable(param.default):
            return param.default()
        return param.default
