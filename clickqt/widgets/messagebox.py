from PySide6.QtWidgets import QMessageBox, QWidget
from clickqt.widgets.base_widget import BaseWidget
from click import Parameter

class MessageBox(BaseWidget):
    widget_type = QWidget

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)

        self.layout.removeWidget(self.label)
        self.layout.removeWidget(self.widget)
        self.label.deleteLater()
        self.container.deleteLater()
        self.container = self.widget
        self.container.setVisible(False)

    def setValue(self, value: bool):
        if isinstance(value, bool):
            self.yes = value
    
    def getWidgetValue(self) -> bool:
        if QMessageBox.information(self.widget, "Confirmation", str(self.param.prompt), 
                                   QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            return True
        else:
            return False