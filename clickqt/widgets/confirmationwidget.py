from PySide6.QtWidgets import QVBoxLayout, QWidget
from clickqt.widgets.basewidget import BaseWidget
from typing import Tuple, Any, Callable
from clickqt.core.error import ClickQtError
from click import Parameter, ParamType

class ConfirmationWidget(BaseWidget):
    widget_type = QWidget

    def __init__(self, otype:ParamType, param:Parameter, default:Any, widgetsource:Callable[[Any], BaseWidget], *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        assert hasattr(self.param, "confirmation_prompt") and self.param.confirmation_prompt
        
        self.param.confirmation_prompt = False  # Stop recursion
        self.field: BaseWidget = widgetsource(self.type, param, default, parent=self, *args, **kwargs)
        kwargs["label"] = "Confirmation "
        self.confirmation_field: BaseWidget = widgetsource(self.type, param, default, parent=self, *args, **kwargs)
        self.param.confirmation_prompt = True
        self.widget.setLayout(QVBoxLayout())
        self.layout.removeWidget(self.label)
        self.layout.removeWidget(self.widget)
        self.label.deleteLater()
        self.container.deleteLater()
        self.container = self.widget
        self.widget.layout().addWidget(self.field.container)
        self.widget.layout().addWidget(self.confirmation_field.container)

    def setValue(self, value):
        self.field.setValue(value)
        self.confirmation_field.setValue(value)

    def handleValid(self, valid: bool):
        self.field.handleValid(valid)
        self.confirmation_field.handleValid(valid)      

    def isEmpty(self) -> bool:
        return self.field.isEmpty() and self.confirmation_field.isEmpty() # If only one is empty (=inputs are different), clickqt rejects it

    def getValue(self) -> Tuple[str, ClickQtError]:
        val1, err1 = self.field.getValue()
        val2, err2 = self.confirmation_field.getValue()

        if err1.type != ClickQtError.ErrorType.NO_ERROR or err2.type != ClickQtError.ErrorType.NO_ERROR:
            return (None, err1 if err1.type != ClickQtError.ErrorType.NO_ERROR else err2)

        if val1 != val2:
            self.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.CONFIRMATION_INPUT_NOT_EQUAL_ERROR, self.widget_name))
        else:
            self.handleValid(True)
            return (val1, ClickQtError())  

        
    def getWidgetValue(self) -> Any:
        return self.field.getWidgetValue()
    