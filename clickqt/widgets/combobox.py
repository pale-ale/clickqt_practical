from typing import Any
from typing import Iterable
from PySide6.QtWidgets import QComboBox
from click import Parameter, ParamType, Context
from clickqt.widgets.basewidget import ComboBoxBase, BaseWidget
from clickqt.widgets.core.QCheckableCombobox import QCheckableComboBox



class ComboBox(ComboBoxBase):
    """Represents a click.types.Choice object.

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QComboBox  #: The Qt-type of this widget.

    def __init__(self, otype: ParamType, param: Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        if (
            self.parent_widget is None
            and (default := BaseWidget.getParamDefault(param, None)) is not None
        ):
            self.setValue(default)

    def setValue(self, value: Any):
        self.widget.setCurrentText(
            str(
                self.type.convert(
                    str(value), self.click_command, Context(self.click_command)
                )
            )
        )

    def addItems(self, items: Iterable[str]):
        self.widget.addItems(items)

    def getWidgetValue(self) -> str:
        return self.widget.currentText()


class CheckableComboBox(ComboBoxBase):
    """Represents a multiple click.types.Choice object.

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QCheckableComboBox  #: The Qt-type of this widget.

    def __init__(self, otype: ParamType, param: Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert param.multiple, "'param.multiple' should be True"

        if self.parent_widget is None:
            self.setValue(BaseWidget.getParamDefault(param, []))

    def setValue(self, value: Iterable[Any]):
        check_values: list[str] = []
        for v in value:
            check_values.append(
                str(
                    self.type.convert(
                        str(v), self.click_command, Context(self.click_command)
                    )
                )
            )

        self.widget.checkItems(check_values)

    def addItems(self, items: Iterable[str]):
        self.widget.addItems(items)

    # def isEmpty(self) -> bool:
    #    return len(self.getWidgetValue()) == 0

    def getWidgetValue(self) -> Iterable[str]:
        return self.widget.getData()
