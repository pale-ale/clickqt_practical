from typing import Any
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout

class BaseWidget(ABC):
    # The type of this widget
    widget_type: Any

    def __init__(self, options, *args, **kwargs):
        self._options = options
        self.container = QWidget()
        self.layout = QHBoxLayout()
        self.label = QLabel(text=f"{options.get('name', 'Unknown')}: ")
        self.label.setToolTip(options.get("help", "No options available"))
        self.widget = self.createWidget(args, kwargs)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.widget)
        self.container.setLayout(self.layout)

    def createWidget(self, *args, **kwargs):
        return self.widget_type()   

    @abstractmethod
    def setValue(self, value):
        pass

    @abstractmethod
    def getValue(self):
        pass


class NumericField(BaseWidget):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.setValue(options.get("default")() if callable(options.get("default")) \
                else options.get("default") or 0)

    def setValue(self, value: int|float):
        self.widget.setValue(value)

    def setMinimum(self, value: int|float):
        self.widget.setMinimum(value)

    def setMaximum(self, value: int|float):
         self.widget.setMaximum(value)


    def getMinimum(self) -> int|float:
        self.widget.minimum()

    def getMaximum(self) -> int|float:
        self.widget.maximum()

    def getValue(self) -> int|float:
        return self.widget.value()

class CheckBoxBase(BaseWidget):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.addItems(options.get("type").get("choices"))
        
    def setValue(self, value: str):
        self.widget.setCurrentText(value)

    @abstractmethod
    def addItems(self, items):
        pass
    