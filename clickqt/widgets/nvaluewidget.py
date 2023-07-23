from typing import Any, Optional, Tuple
from collections.abc import Callable, Iterable
from click import Context, Parameter, ParamType, Choice
from PySide6.QtWidgets import QVBoxLayout, QScrollArea, QPushButton, QWidget
from PySide6.QtCore import Qt

from clickqt.widgets.basewidget import BaseWidget, MultiWidget
from clickqt.core.error import ClickQtError


class NValueWidget(MultiWidget):
    """Represents a multiple click.Parameter-object.
    The child widgets are set according to :func:`~clickqt.widgets.basewidget.MultiWidget.init`.

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param widgetsource: A reference to :func:`~clickqt.core.gui.GUI.createWidget`
    :param parent: The parent BaseWidget of **otype**, defaults to None. Needed for :class:`~clickqt.widgets.basewidget.MultiWidget`-widgets
    :param kwargs: Additionally parameters ('com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QScrollArea  #: The Qt-type of this widget.

    def __init__(
        self,
        otype: ParamType,
        param: Parameter,
        widgetsource: Callable[[Any], BaseWidget],
        parent: Optional[BaseWidget] = None,
        **kwargs,
    ):
        super().__init__(otype, param, parent=parent, **kwargs)

        assert not isinstance(
            otype, Choice
        ), f"'otype' is of type '{Choice}', but there is a better version for this type"
        assert param.multiple, "'param.multiple' should be True"

        self.widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.optkwargs = kwargs
        self.widgetsource = widgetsource
        self.vbox = QWidget()
        self.vbox.setLayout(QVBoxLayout())
        self.widget.setWidgetResizable(True)
        addfieldbtn = QPushButton("+", self.widget)
        addfieldbtn.clicked.connect(lambda: self.addPair())  # Add an empty widget
        self.vbox.layout().addWidget(addfieldbtn)
        self.widget.setWidget(self.vbox)
        self.buttondict: dict[QPushButton, BaseWidget] = {}

        self.children = self.buttondict.values()

        self.init()

    def addPair(self, value: Any = None):
        """Adds a new (child-)widget of type **otype** with a remove button to this widget.
        If **value** is not None, it will be the initial value of the new added widget.

        :param value: The initial value of the new widget, defaults to None (=widget will be zero initialized)
        """

        if len(self.children) == 0:
            self.handleValid(True)

        self.param.multiple = (
            False  # nargs cannot be nested, so it is safe to turn this off for children
        )
        clickqtwidget: BaseWidget = self.widgetsource(
            self.type,
            self.param,
            widgetsource=self.widgetsource,
            parent=self,
            **self.optkwargs,
        )
        self.param.multiple = True  # click needs this for a correct conversion
        if value is not None:
            clickqtwidget.setValue(value)
        clickqtwidget.layout.removeWidget(clickqtwidget.label)
        clickqtwidget.label.deleteLater()
        removebtn = QPushButton("-", clickqtwidget.widget)
        clickqtwidget.layout.addWidget(removebtn)
        removebtn.clicked.connect(lambda: self.removeButtonPair(removebtn))
        self.vbox.layout().addWidget(clickqtwidget.container)
        self.buttondict[removebtn] = clickqtwidget
        self.widget.setWidget(self.vbox)

    def removeButtonPair(self, btn_to_remove: QPushButton):
        """Removes the widget assoziated with **btn_to_remove**.

        :param btn_to_remove: The remove-button that was clicked
        """

        if btn_to_remove in self.buttondict:
            cqtwidget = self.buttondict.pop(btn_to_remove)
            self.vbox.layout().removeWidget(cqtwidget.container)
            cqtwidget.layout.removeWidget(cqtwidget.widget)
            cqtwidget.container.deleteLater()
            btn_to_remove.deleteLater()
            QScrollArea.updateGeometry(self.widget)

    def getValue(self) -> Tuple[Any, ClickQtError]:
        """Validates the value of the children-widgets and returns the result. If multiple errors occured then they will be concatenated and returned.

        :return: Valid: (children-widget values or the value of a callback, :class:`~clickqt.core.error.ClickQtError.ErrorType.NO_ERROR`)\n
                 Invalid: (None, :class:`~clickqt.core.error.ClickQtError.ErrorType.CONVERTING_ERROR` or
                 :class:`~clickqt.core.error.ClickQtError.ErrorType.PROCESSING_VALUE_ERROR` or :class:`~clickqt.core.error.ClickQtError.ErrorType.REQUIRED_ERROR`)
        """

        value_missing = False
        if len(self.children) == 0:
            default = BaseWidget.getParamDefault(self.param, None)

            if self.param.required and default is None:
                self.handleValid(False)
                return (
                    None,
                    ClickQtError(
                        ClickQtError.ErrorType.REQUIRED_ERROR,
                        self.widget_name,
                        self.param.param_type_name,
                    ),
                )
            if (
                envvar_values := self.param.value_from_envvar(
                    Context(self.click_command)
                )
            ) is not None:
                for ev in envvar_values:
                    self.addPair(ev)
            elif default is not None:  # Add new pairs
                for (
                    value
                ) in (
                    default
                ):  # All defaults will be considered if len(self.children)) == 0
                    self.addPair(value)
            else:  # param is not required and there is no default -> value is None
                value_missing = True  # But callback should be considered

        values: "Iterable|None" = None

        if not value_missing:
            values = []
            err_messages: list[str] = []
            default = BaseWidget.getParamDefault(self.param, None)

            # len(self.children)) < len(default): We set at most len(self.children)) defaults
            # len(self.children)) >= len(default): All defaults will be considered
            for i, child in enumerate(self.children):
                try:  # Try to convert the provided value into the corresponding click object type
                    if child.isEmpty():
                        if child.param.required and default is None:
                            self.handleValid(False)
                            return (
                                None,
                                ClickQtError(
                                    ClickQtError.ErrorType.REQUIRED_ERROR,
                                    child.widget_name,
                                    child.param.param_type_name,
                                ),
                            )
                        if default is not None and i < len(
                            default
                        ):  # Overwrite the empty widget with the default value (if one exists)
                            child.setValue(
                                default[i]
                            )  # If the widget is a tuple, all values will be overwritten
                        else:  # No default exists -> Don't consider the value of this child
                            # We can't remove the child because there would be a problem with out-of-focus-validation when
                            # having multiple string based widgets (the validator would remove the widget before all child-widgets could be filled)
                            continue

                    values.append(
                        self.type.convert(
                            value=child.getWidgetValue(),
                            param=self.param,
                            ctx=Context(self.click_command),
                        )
                    )
                    child.handleValid(True)
                except Exception as e:
                    child.handleValid(False)
                    err_messages.append(str(e))

            if len(err_messages) > 0:  # Join all error messages and return them
                messages = ", ".join(err_messages)
                return (
                    None,
                    ClickQtError(
                        ClickQtError.ErrorType.CONVERTING_ERROR,
                        self.widget_name,
                        messages
                        if len(err_messages) == 1
                        else messages.join(["[", "]"]),
                    ),
                )

            if len(values) == 0:  # All widgets are empty
                values = None

        return self.handleCallback(values)

    def setValue(self, value: Iterable[Any]):
        """Sets the values of the (child-)widgets.
        The number of (child-)widgets are adjusted to the length of **value**. This means that (child-)widgets may be added, but also removed.

        :param value: The list of new values that should be stored in the (child-)widgets
        """

        if len(value) < len(self.children):  # Remove pairs
            for btns in list(self.buttondict.keys())[len(value) :]:
                self.removeButtonPair(btns)
        if len(value) > len(self.children):  # Add pairs
            for i in range(len(value) - len(self.children)):
                self.addPair()

        for i, c in enumerate(self.children):  # Set the value
            c.setValue(value[i])

    def handleValid(self, valid: bool):
        if len(self.children) == 0:
            BaseWidget.handleValid(self, valid)
        else:
            super().handleValid(valid)
