from PySide6.QtWidgets import QVBoxLayout, QWidget
from clickqt.widgets.base_widget import BaseWidget
from typing import Tuple, Any, Callable
from clickqt.core.error import ClickQtError

class ConfirmationWidget(BaseWidget):
    widget_type = QWidget

    def __init__(self, options, widgetsource:Callable[[Any], BaseWidget], *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        assert hasattr(self.click_object, "confirmation_prompt") and self.click_object.confirmation_prompt
        
        self.click_object.confirmation_prompt = False  # Stop recursion
        self.field: BaseWidget = widgetsource(self.click_object.type, options, parent=self, *args, **kwargs)
        kwargs["label"] = "Confirmation "
        self.confirmation_field: BaseWidget = widgetsource(self.click_object.type, options, parent=self, *args, **kwargs)
        self.widget.setLayout(QVBoxLayout())
        self.layout.removeWidget(self.label)
        self.layout.removeWidget(self.widget)
        self.label.deleteLater()
        self.container.deleteLater()
        self.container = self.widget
        self.widget.layout().addWidget(self.field.container)
        self.widget.layout().addWidget(self.confirmation_field.container)

    def setValue(self, value: tuple|list):
        assert len(value) == 2
        self.field.setValue(value[0])
        self.confirmation_field.setValue(value[1])

    def handleValid(self, valid: bool):
        self.field.handleValid(valid)
        self.confirmation_field.handleValid(valid)      

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
   