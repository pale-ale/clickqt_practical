from PySide6.QtWidgets import QVBoxLayout, QScrollArea, QPushButton, QWidget
from PySide6.QtCore import Qt
from clickqt.widgets.base_widget import BaseWidget
from clickqt.widgets.tuplewidget import TupleWidget
from typing import Any, Callable, Tuple, List
from clickqt.core.error import ClickQtError
from click import Context

class NValueWidget(BaseWidget):
    widget_type = QScrollArea
    
    def __init__(self, options, widgetsource:Callable[[Any], BaseWidget], parent: BaseWidget = None, *args, **kwargs):
        super().__init__(options, parent, *args, **kwargs)
        self.widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy(0x2))
        self.options = options
        self.optargs = args
        self.optkwargs = kwargs
        self.optiontype = self.click_object.type
        self.widgetsource = widgetsource
        self.vbox = QWidget()
        self.vbox.setLayout(QVBoxLayout())
        self.widget.setWidgetResizable(True)
        addfieldbtn = QPushButton("+", self.widget)
        addfieldbtn.clicked.connect(self.add_empty_pair)
        self.vbox.layout().addWidget(addfieldbtn)
        self.widget.setWidget(self.vbox)
        self.buttondict:dict[QPushButton, BaseWidget] = dict()
    
    def add_empty_pair(self):
        self.click_object.multiple = False # nargs cannot be nested, so it is safe to turn this off for children
        clickqtwidget:BaseWidget = self.widgetsource(self.optiontype, self.options, *self.optargs, widgetsource=self.widgetsource, parent=self, **self.optkwargs)
        self.click_object.multiple = True # click needs this for a correct conversion
        clickqtwidget.layout.removeWidget(clickqtwidget.label)
        clickqtwidget.label.deleteLater()
        removebtn = QPushButton("-", clickqtwidget.widget)
        clickqtwidget.layout.addWidget(removebtn)
        removebtn.clicked.connect(lambda: self.remove_button_pair(removebtn))
        self.vbox.layout().addWidget(clickqtwidget.container)
        self.buttondict[removebtn] = clickqtwidget
        self.widget.setWidget(self.vbox)
    
    def remove_button_pair(self, btntoremove):
        if btntoremove in self.buttondict:
            cqtwidget = self.buttondict.pop(btntoremove)
            self.vbox.layout().removeWidget(cqtwidget.container)
            cqtwidget.layout.removeWidget(cqtwidget.widget)
            cqtwidget.container.deleteLater()
            btntoremove.deleteLater()
            QScrollArea.updateGeometry(self.widget)

    def handleValid(self, valid: bool):
        for c in self.buttondict.values():
            if not isinstance(c, TupleWidget):
                BaseWidget.handleValid(c, valid)
            else:
                c.handleValid(valid) # Recursive

    def getValue(self) -> Tuple[Any, ClickQtError]:
        values = []
        err_messages: List[str] = []
        for child in self.buttondict.values():
            try: # Try to convert the provided value into the corresponding click object type
                values.append(self.click_object.type.convert(value=child.getWidgetValue(), param=self.click_object, ctx=Context(self.click_command))) 
                child.handleValid(True)
            except Exception as e:
                child.handleValid(False)
                err_messages.append(str(e))
            
        if len(err_messages): # Join all error messages and return them
            messages = ", ".join(err_messages) 
            return (None, ClickQtError(ClickQtError.ErrorType.CONVERTION_ERROR, self.widget_name, messages if len(err_messages) == 1 else messages.join(["[", "]"])))
            
        try: # Consider callbacks
            ret_val = (self.click_object.process_value(Context(self.click_command), values), ClickQtError())
            self.handleValid(True)
            return ret_val
        except Exception as e:
            self.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.CALLBACK_VALIDATION_ERROR, self.widget_name, e))

    def setValue(self, value):
        raise NotImplementedError()
    
    def getWidgetValue(self) -> list[Any]:
        return [c.getWidgetValue() for c in self.buttondict.values()]