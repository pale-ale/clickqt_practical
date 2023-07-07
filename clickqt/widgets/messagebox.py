from typing import Any
from PySide6.QtWidgets import QMessageBox, QWidget
from clickqt.core.error import ClickQtError
from clickqt.widgets.basewidget import BaseWidget
from click import Parameter, ParamType, Context

class MessageBox(BaseWidget):
    widget_type = QWidget

    def __init__(self, otype:ParamType, param:Parameter, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        assert hasattr(param, "is_flag") and param.is_flag, "'param.is_flag' should be True" 
        assert hasattr(param, "prompt") and param.prompt, "'param.prompt' should be not empty"

        self.yes:bool = False

        if self.parent_widget is None:
            self.setValue(BaseWidget.getParamDefault(param, False))

        self.layout.removeWidget(self.label)
        self.layout.removeWidget(self.widget)
        self.label.deleteLater()
        self.container.deleteLater()
        self.container = self.widget
        self.container.setVisible(False)

    def setValue(self, value:Any):
        self.yes = bool(self.type.convert(str(value), self.click_command, Context(self.click_command)))
    
    def getValue(self) -> tuple[Any, ClickQtError]:
        if QMessageBox.information(self.widget, "Confirmation", str(self.param.prompt), 
                                   QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            self.yes = True
        else:
            self.yes = False
        
        return super().getValue()
    
    def getWidgetValue(self) -> bool:
        return self.yes