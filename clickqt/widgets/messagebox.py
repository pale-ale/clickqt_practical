from typing import Any
from PySide6.QtWidgets import QMessageBox, QWidget
from clickqt.core.error import ClickQtError
from clickqt.widgets.basewidget import BaseWidget
from click import Parameter, ParamType, Context

class MessageBox(BaseWidget):
    widget_type = QWidget

    def __init__(self, otype:ParamType, param:Parameter, default:Any, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        self.yes:bool

        self.setValue(default if default is not None else False)

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