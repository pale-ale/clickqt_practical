from typing import Any, Optional
from typing import Callable
from click import Parameter, ParamType, Tuple as ClickTuple
from PySide6.QtWidgets import QGroupBox, QHBoxLayout

from clickqt.widgets.basewidget import BaseWidget, MultiWidget


class TupleWidget(MultiWidget):
    """Represents a click.types.Tuple-object.
    The child widgets are set according to :func:`~clickqt.widgets.basewidget.MultiWidget.init`.

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param widgetsource: A reference to :func:`~clickqt.core.gui.GUI.createWidget`
    :param parent: The parent BaseWidget of **otype**, defaults to None. Needed for :class:`~clickqt.widgets.basewidget.MultiWidget`-widgets
    :param kwargs: Additionally parameters ('com', 'label') needed for
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QGroupBox  #: The Qt-type of this widget.

    def __init__(
        self,
        otype: ParamType,
        param: Parameter,
        widgetsource: Callable[[Any], BaseWidget],
        parent: Optional[BaseWidget] = None,
        **kwargs,
    ):
        super().__init__(otype, param, parent=parent, **kwargs)

        assert isinstance(
            otype, ClickTuple
        ), f"'otype' must be of type '{ClickTuple}', but is '{type(otype)}'."
        assert otype.is_composite, "otype.is_composite should be True"

        self.widget.setLayout(QHBoxLayout())

        for t in otype.types if hasattr(otype, "types") else otype:
            nargs = self.param.nargs
            self.param.nargs = 1
            bw: BaseWidget = widgetsource(
                t, self.param, widgetsource=widgetsource, parent=self, **kwargs
            )
            self.param.nargs = nargs
            bw.layout.removeWidget(bw.label)
            bw.label.deleteLater()
            self.widget.layout().addWidget(bw.container)
            self.children.append(bw)

        self.init()
