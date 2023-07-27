from __future__ import annotations

from abc import ABC, abstractmethod
import os
import typing as t
from gettext import ngettext

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
import click

from clickqt.core.error import ClickQtError
import clickqt.core  # FocusOutValidator


class BaseWidget(ABC):
    """Provides basic functionalities and initializes the widget.
    Every clickqt widget has to inherit from this class.

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param parent: The parent BaseWidget of **otype**, defaults to None. Needed for :class:`~clickqt.widgets.basewidget.MultiWidget`-widgets
    :param kwargs: Additionally parameters ('widgetsource', 'com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type: t.ClassVar[t.Type]  #: The Qt-type of this widget.

    def __init__(
        self,
        otype: click.ParamType,
        param: click.Parameter,
        parent: t.Optional["BaseWidget"] = None,
        **kwargs,
    ):
        assert isinstance(otype, click.ParamType)
        assert isinstance(param, click.Parameter)
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

        self.widget.setObjectName(
            param.name
        )  # Only change the stylesheet of this widget and not of all (child-)widgets

        assert self.widget is not None, "Widget not initialized"
        assert self.param is not None, "Click param object not provided"
        assert self.click_command is not None, "Click command not provided"
        assert self.type is not None, "Type not provided"

        self.focus_out_validator = clickqt.core.FocusOutValidator(self)
        self.widget.installEventFilter(self.focus_out_validator)

    def create_widget(self) -> QWidget:
        """Creates the widget specified in :attr:`~clickqt.widgets.basewidget.BaseWidget.widget_type` and returns it."""

        return self.widget_type()

    @abstractmethod
    def set_value(self, value: t.Any):
        """Sets the value of the Qt-widget.

        :param value: The new value that should be stored in the widget
        :raises click.BadParameter: **value** could not be converted into the corresponding click.ParamType
        """

    def is_empty(self) -> bool:
        """Checks whether the widget is empty. This can be the case for string-based widgets or the
        multiple choice-widget (:class:`~clickqt.widgets.combobox.CheckableComboBox`).\n
        Subclasses may need to override this method.

        :return: False
        """
        return False

    def get_value(self) -> tuple[t.Any, ClickQtError]:
        """Validates the value of the Qt-widget and returns the result.

        :return: Valid: (widget value or the value of a callback, :class:`~clickqt.core.error.ClickQtError.ErrorType.NO_ERROR`)\n
                 Invalid: (None, :class:`~clickqt.core.error.ClickQtError.ErrorType.CONVERTING_ERROR` or
                 :class:`~clickqt.core.error.ClickQtError.ErrorType.PROCESSING_VALUE_ERROR` or :class:`~clickqt.core.error.ClickQtError.ErrorType.REQUIRED_ERROR`)
        """
        value: t.Any = None

        # Try to convert the provided value into the corresponding click object type
        try:  # pylint: disable=too-many-try-statements, too-many-nested-blocks
            default = BaseWidget.get_param_default(self.param, None)
            # if statement is obtained by creating the corresponding truth table
            if self.param.multiple or (
                not isinstance(self.type, click.Tuple) and self.param.nargs != 1
            ):
                value_missing = False
                widget_values: list = self.get_widget_value()

                if len(widget_values) == 0:  # Checkable combobox
                    if self.param.required and default is None:
                        self.handle_valid(False)
                        return (
                            None,
                            ClickQtError(
                                ClickQtError.ErrorType.REQUIRED_ERROR,
                                self.widget_name,
                                self.param.param_type_name,
                            ),
                        )
                    #self.handle_parameter_missing_default(default)
                    if default is not None:
                        self.set_value(default)
                        widget_values = self.get_widget_value()
                    else:  # param is not required and there is no default -> value is None
                        value_missing = True  # But callback should be considered

                if not value_missing:
                    value = []
                    for i, v in enumerate(
                        widget_values
                    ):  # v is not a BaseWidget, but a primitive type
                        if (
                            str(v) == ""
                        ):  # Empty widget (only possible for string based widgets)
                            if self.param.required and default is None:
                                self.handle_valid(False)
                                return (
                                    None,
                                    ClickQtError(
                                        ClickQtError.ErrorType.REQUIRED_ERROR,
                                        self.widget_name,
                                        self.param.param_type_name,
                                    ),
                                )
                            if default is not None and i < len(
                                default
                            ):  # Overwrite the empty widget with the default value and execute with this (new) value
                                values = self.get_widget_value()
                                values[i] = default[
                                    i
                                ]  # Only overwrite the empty widget, not all
                                self.set_value(values)
                                v = default[i]
                            else:  # param is not required, widget is empty and there is no default (click equivalent: option not provided in click command cmd)
                                value = None
                                break

                        value.append(
                            self.type.convert(
                                value=v,
                                param=self.param,
                                ctx=click.Context(self.click_command),
                            )
                        )
            else:
                value_missing = False
                if self.is_empty():
                    if self.param.required and default is None:
                        self.handle_valid(False)
                        return (
                            None,
                            ClickQtError(
                                ClickQtError.ErrorType.REQUIRED_ERROR,
                                self.widget_name,
                                self.param.param_type_name,
                            ),
                        )
                    if default is not None:
                        self.set_value(default)
                    else:
                        value_missing = True  # -> value is None

                if not value_missing:
                    value = self.type.convert(
                        value=self.get_widget_value(),
                        param=self.param,
                        ctx=click.Context(self.click_command),
                    )
        except Exception as e: # pylint: disable=broad-exception-caught
            self.handle_valid(False)
            return (
                None,
                ClickQtError(
                    ClickQtError.ErrorType.CONVERTING_ERROR, self.widget_name, e
                ),
            )

        return self.handle_callback(value)

    def handle_callback(self, value: t.Any) -> tuple[t.Any, ClickQtError]:
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
        except Exception as e: # pylint: disable=broad-exception-caught
            self.handle_valid(False)
            return (
                None,
                ClickQtError(
                    ClickQtError.ErrorType.PROCESSING_VALUE_ERROR, self.widget_name, e
                ),
            )

    @abstractmethod
    def get_widget_value(self) -> t.Any:
        """Returns the value of the Qt-widget without any checks."""

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

    @staticmethod
    def get_param_default(param: click.Parameter, alternative:t.Any=None):
        """Returns the default value of **param**. If there is no default value, **alternative** will be returned."""

        # TODO: Replace with param.get_default(ctx=click.Context(command), call=True)
        if param.default is None:
            return alternative
        if callable(param.default):
            return param.default()
        return param.default


class NumericField(BaseWidget):
    """Provides basic functionalities for numeric based widgets

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    def set_value(self, value: t.Any):
        self.widget.setValue(
            self.type.convert(
                value=str(value),
                param=self.click_command,
                ctx=click.Context(self.click_command),
            )
        )

    def set_minimum(self, minval: t.Union[int, float]):
        """Sets the minimum value."""

        self.widget.setMinimum(minval)

    def set_maximum(self, maxval: t.Union[int, float]):
        """Sets the maximum value."""

        self.widget.setMaximum(maxval)

    def get_widget_value(self) -> t.Union[int, float]:
        return self.widget.value()


class ComboBoxBase(BaseWidget):
    """Provides basic functionalities for click.types.Choice based widgets

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    def __init__(self, otype: click.ParamType, param: click.Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert isinstance(
            otype, click.Choice
        ), f"'otype' must be of type '{click.Choice}', but is '{type(otype)}'."

        self.add_items(otype.choices)

    @abstractmethod
    def add_items(self, items: t.Iterable[str]):
        """Adds each of the strings in **items** to the checkable combobox."""


class MultiWidget(BaseWidget):
    """Provides basic functionalities for click.types.CompositeParamType based widgets and multi value widgets.

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    def __init__(self, otype: click.ParamType, param: click.Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        self.children: t.Union[t.Iterable[BaseWidget],t.dict_values[BaseWidget]] = []

    def init(self):
        """Sets the value of the (child-)widgets according to envvar or default values.
        If the envvar values are None, the defaults values will be considered.
        """

        if self.parent_widget is None:
            # Consider envvar
            if (
                envvar_values := self.param.resolve_envvar_value(
                    click.Context(self.click_command)
                )
            ) is not None:
                # self.type.split_envvar_value(envvar_values) does not work because clicks "self.envvar_list_splitter" is not set corrently
                self.set_value(envvar_values.split(os.path.pathsep))
            elif (
                default := BaseWidget.get_param_default(self.param, None)
            ) is not None:  # Consider default value
                self.set_value(default)

    def set_value(self, value: t.Iterable[t.Any]):
        if len(value) != self.param.nargs:
            raise click.BadParameter(
                ngettext(
                    "Takes {nargs} values but 1 was given.",
                    "Takes {nargs} values but {len} were given.",
                    len(value),
                ).format(nargs=self.param.nargs, len=len(value)),
                ctx=click.Context(self.click_command),
                param=self.param,
            )

        for i, c in enumerate(self.children):
            c.set_value(value[i])

    def handle_valid(self, valid: bool):
        for c in self.children:
            c.handle_valid(valid)

    def is_empty(self) -> bool:
        """ "Checks whether the widget is empty. This is the case when there are no children or when at least one (string-based) children is empty.

        :return: True, if this widget has no children or at least one children is empty, False otherwise
        """

        if len(self.children) == 0:
            return True

        return any([c.is_empty() for c in self.children])

    def get_widget_value(self) -> t.Iterable[t.Any]:
        return [c.get_widget_value() for c in self.children]
