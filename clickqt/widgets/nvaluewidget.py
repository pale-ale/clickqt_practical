from PySide6.QtWidgets import QVBoxLayout, QScrollArea, QPushButton, QWidget
from PySide6.QtCore import Qt
from clickqt.widgets.base_widget import BaseWidget
from clickqt.widgets.tuplewidget import TupleWidget
from typing import Any, Callable, Tuple, List
from clickqt.core.error import ClickQtError
from click import Context, Parameter, Abort

class NValueWidget(BaseWidget):
    widget_type = QScrollArea
    
    def __init__(self, param:Parameter, widgetsource:Callable[[Any], BaseWidget], parent: BaseWidget = None, *args, **kwargs):
        super().__init__(param, parent, *args, **kwargs)
        self.widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy(0x2))
        self.optargs = args
        self.optkwargs = kwargs
        self.widgetsource = widgetsource
        self.vbox = QWidget()
        self.vbox.setLayout(QVBoxLayout())
        self.widget.setWidgetResizable(True)
        addfieldbtn = QPushButton("+", self.widget)
        addfieldbtn.clicked.connect(lambda: self.addPair()) # Add an empty widget
        self.vbox.layout().addWidget(addfieldbtn)
        self.widget.setWidget(self.vbox)
        self.buttondict:dict[QPushButton, BaseWidget] = dict()

        # Consider envvar
        if (envvar_value := self.param.resolve_envvar_value(Context(self.click_command))) is not None:
            for value in self.param.type.split_envvar_value(envvar_value):
                if value: # Don't add empty widgets
                    self.addPair(value)
        else: # Consider default value
            if len(default := BaseWidget.getParamDefault(self.param, [])):
                for value in default:
                    self.addPair(value)
        
    def addPair(self, value = None):
        self.param.multiple = False # nargs cannot be nested, so it is safe to turn this off for children
        clickqtwidget:BaseWidget = self.widgetsource(self.param.type, self.param, *self.optargs, widgetsource=self.widgetsource, parent=self, **self.optkwargs)
        self.param.multiple = True # click needs this for a correct conversion
        if value is not None:
            clickqtwidget.setValue(value)
        clickqtwidget.layout.removeWidget(clickqtwidget.label)
        clickqtwidget.label.deleteLater()
        removebtn = QPushButton("-", clickqtwidget.widget)
        clickqtwidget.layout.addWidget(removebtn)
        removebtn.clicked.connect(lambda: self.removeButtonPair(removebtn))
        self.vbox.layout().addWidget(clickqtwidget.container)
        self.buttondict[removebtn] = clickqtwidget
        self.widget.setWidget(self.vbox)
    
    def removeButtonPair(self, btntoremove):
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
        value_missing = False
        if len(self.buttondict.values()) == 0:
            default = BaseWidget.getParamDefault(self.param, None)
            if self.param.required and default is None:
                self.handleValid(False)
                return (None, ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR, self.widget_name, self.param.param_type_name))
            elif default is not None: # Add new pairs
                for value in default: # All defaults will be considered if len(self.buttondict.values()) == 0
                    self.addPair(value)
            else: # param is not required and there is no default -> value is None
                value_missing = True # But callback should be considered

        values: list|None = None
        
        if not value_missing:
            values = []
            err_messages: List[str] = []
            default = BaseWidget.getParamDefault(self.param, None)

            # len(self.buttondict.items()) < len(default): We set at most len(self.buttondict.items()) defaults
            # len(self.buttondict.items()) >= len(default): All defaults will be considered
            for i, child in enumerate(self.buttondict.values()):
                try: # Try to convert the provided value into the corresponding click object type
                    if child.isEmpty():
                        if child.param.required and default is None:
                            self.handleValid(False)
                            return (None, ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR, child.widget_name, child.param.param_type_name))
                        elif default is not None and i < len(default): # Overwrite the empty widget with the default value (if one exists)
                            child.setValue(default[i]) # If the widget is a tuple, all values will be overwritten
                        else: # No default exists -> Don't consider the value of this child
                            # We can't remove the child because there would be a problem with out-of-focus-validation when
                            # having multiple string based widgets (the validator would remove the widget before all child-widgets could be filled)
                            continue
                            
                    values.append(self.param.type.convert(value=child.getWidgetValue(), param=self.param, ctx=Context(self.click_command))) 
                    child.handleValid(True)
                except Exception as e:
                    child.handleValid(False)
                    err_messages.append(str(e))
                
            if len(err_messages) > 0: # Join all error messages and return them
                messages = ", ".join(err_messages) 
                return (None, ClickQtError(ClickQtError.ErrorType.CONVERTING_ERROR, self.widget_name, messages if len(err_messages) == 1 else messages.join(["[", "]"])))
            
            if len(values) == 0: # All widgets are empty
                values = None

        try: # Consider callbacks
            ret_val = (self.param.process_value(Context(self.click_command), values), ClickQtError())
            self.handleValid(True)
            return ret_val
        except Abort as e:
            return (None, ClickQtError(ClickQtError.ErrorType.ABORTED_ERROR))
        except Exception as e:
            self.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.PROCESSING_VALUE_ERROR, self.widget_name, e))

    def setValue(self, value):
        assert len(value) == len(self.buttondict.values())
        for i,c in enumerate(self.buttondict.values()):
            c.setValue(value[i])
    
    def isEmpty(self) -> bool:
        if len(self.buttondict.values()) == 0:
            return True

        for c in self.buttondict.values():
            if c.isEmpty():
                return True
        
        return False
    
    def getWidgetValue(self) -> list[Any]:
        return [c.getWidgetValue() for c in self.buttondict.values()]
    
