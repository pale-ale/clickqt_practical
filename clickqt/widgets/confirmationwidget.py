from typing import Tuple, Any
from typing import Callable
from click import Parameter, ParamType
from PySide6.QtWidgets import QWidget, QHBoxLayout

from clickqt.widgets.basewidget import BaseWidget
from clickqt.core.error import ClickQtError


class ConfirmationWidget(BaseWidget):
    """Represents a click option with confirmation_prompt==True. It stores two clickqt widgets of the same type.

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param widgetsource: A reference to :func:`~clickqt.core.gui.GUI.createWidget`
    :param kwargs: Additionally parameters ('parent', 'com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QWidget  #: The Qt-type of this widget. It's a container for storing the two input-widgets

    def __init__(
        self,
        otype: ParamType,
        param: Parameter,
        widgetsource: Callable[[Any], BaseWidget],
        **kwargs
    ):
        super().__init__(otype, param, **kwargs)

        assert (
            hasattr(self.param, "confirmation_prompt")
            and self.param.confirmation_prompt
        ), "'param.confirmation_prompt' should be True"

        self.param.confirmation_prompt = False  # Stop recursion
        self.field: BaseWidget = widgetsource(
            self.type, param, parent=self, vboxlayout=True, **kwargs
        )  #: First input widget.
        kwargs["label"] = "Confirmation "
        self.confirmation_field: BaseWidget = widgetsource(
            self.type, param, parent=self, vboxlayout=True, **kwargs
        )  #: Second (confirmation) input widget.
        self.param.confirmation_prompt = True
        self.widget.setLayout(QHBoxLayout())
        self.layout.removeWidget(self.label)
        self.layout.removeWidget(self.widget)
        self.label.deleteLater()
        self.container.deleteLater()
        self.container = self.widget
        self.container.layout().setContentsMargins(0, 0, 0, 0)
        self.widget.layout().addWidget(self.field.container)
        self.widget.layout().addWidget(self.confirmation_field.container)

        if self.parent_widget is None:
            self.setValue(BaseWidget.getParamDefault(param, None))

    def setValue(self, value: Any):
        """Sets **value** as widget value for :attr:`~clickqt.widgets.confirmationwidget.ConfirmationWidget.field` and
        :attr:`~clickqt.widgets.confirmationwidget.ConfirmationWidget.confirmation_field` according to :func:`~clickqt.widgets.basewidget.BaseWidget.setValue`."""

        if value is not None:
            self.field.setValue(value)
            self.confirmation_field.setValue(value)

    def handleValid(self, valid: bool):
        """Changes the widget border for :attr:`~clickqt.widgets.confirmationwidget.ConfirmationWidget.field` and
        :attr:`~clickqt.widgets.confirmationwidget.ConfirmationWidget.confirmation_field` according to :func:`~clickqt.widgets.basewidget.BaseWidget.handleValid`."""

        self.field.handleValid(valid)
        self.confirmation_field.handleValid(valid)

    # def isEmpty(self) -> bool:
    #    return self.field.isEmpty() and self.confirmation_field.isEmpty() # If only one is empty (=inputs are different), clickqt rejects it

    def getValue(self) -> Tuple[Any, ClickQtError]:
        """Calls :func:`~clickqt.widgets.basewidget.BaseWidget.getValue` on :attr:`~clickqt.widgets.confirmationwidget.ConfirmationWidget.field` and
        :attr:`~clickqt.widgets.confirmationwidget.ConfirmationWidget.confirmation_field`, validates the result and returns it.

        :return: Valid: (widget value or the value of a callback, :class:`~clickqt.core.error.ClickQtError.ErrorType.NO_ERROR`)\n
                 Invalid: (None, :class:`~clickqt.core.error.ClickQtError.ErrorType.CONVERTING_ERROR` or
                 :class:`~clickqt.core.error.ClickQtError.ErrorType.PROCESSING_VALUE_ERROR` or :class:`~clickqt.core.error.ClickQtError.ErrorType.CONFIRMATION_INPUT_NOT_EQUAL_ERROR`)
        """

        val1, err1 = self.field.getValue()
        val2, err2 = self.confirmation_field.getValue()

        if (
            err1.type != ClickQtError.ErrorType.NO_ERROR
            or err2.type != ClickQtError.ErrorType.NO_ERROR
        ):
            return (
                None,
                err1 if err1.type != ClickQtError.ErrorType.NO_ERROR else err2,
            )

        if val1 != val2:
            self.handleValid(False)
            return (
                None,
                ClickQtError(
                    ClickQtError.ErrorType.CONFIRMATION_INPUT_NOT_EQUAL_ERROR,
                    self.widget_name,
                ),
            )
        self.handleValid(True)
        return (val1, ClickQtError())

    def getWidgetValue(self) -> Any:
        return self.field.getWidgetValue()
