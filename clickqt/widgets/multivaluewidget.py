from __future__ import annotations

import typing as t

import click
from PySide6.QtWidgets import QGroupBox, QVBoxLayout

from clickqt.widgets.basewidget import BaseWidget, MultiWidget


class MultiValueWidget(MultiWidget):
    """Represents a multi value click option with a fixed number of types (**param**.nargs >=2).
    The child widgets are set according to :func:`~clickqt.widgets.basewidget.MultiWidget.init`.

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param widgetsource: A reference to :func:`~clickqt.core.gui.GUI.create_widget`
    :param parent: The parent BaseWidget of **otype**, defaults to None. Needed for :class:`~clickqt.widgets.basewidget.MultiWidget`-widgets
    :param kwargs: Additionally parameters ('com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QGroupBox  #: The Qt-type of this widget.

    def __init__(
        self,
        otype: click.ParamType,
        param: click.Parameter,
        widgetsource: t.Callable[[t.Any], BaseWidget],
        parent: t.Optional[BaseWidget] = None,
        **kwargs,
    ):
        super().__init__(otype, param, parent=parent, **kwargs)

        assert (
            param.nargs >= 2
        ), f"'param.nargs' should be >= 2, but is '{param.nargs}'."

        self.widget.setLayout(QVBoxLayout())

        # Add param.nargs widgets of type otype
        for _ in range(param.nargs):
            nargs = param.nargs
            param.nargs = 1  # Stop recursion
            bw: BaseWidget = widgetsource(
                otype, param, widgetsource=widgetsource, parent=self, **kwargs
            )
            param.nargs = nargs  # click needs the right value for a correct conversion
            bw.layout.removeWidget(bw.label)
            bw.label.deleteLater()
            self.widget.layout().addWidget(bw.container)
            self.children.append(bw)

        self.init()
