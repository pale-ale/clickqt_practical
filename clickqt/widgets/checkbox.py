from PySide6.QtWidgets import QCheckBox
from clickqt.widgets.base_widget import BaseWidget
from typing import Tuple
from clickqt.core.error import ClickQtError

class CheckBox(BaseWidget):
    widget_type = QCheckBox

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.setValue(options.get("default")() if callable(options.get("default")) \
                else options.get("default") or False)

    def setValue(self, value: bool):
        self.widget.setChecked(value)

    def getValue(self) -> Tuple[bool, ClickQtError]:
        value, err = self.callback_validate()
        if err.type != ClickQtError.ErrorType.NO_ERROR:
            self.handleValid(False)
            return (value, err)
        
        return (self.getWidgetValue(), ClickQtError())
    
    def getWidgetValue(self) -> bool:
        return self.widget.isChecked()
    