from typing import Any, ClassVar, Type
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from clickqt.core.error import ClickQtError
import clickqt.core # FocusOutValidator
from click import Context, Parameter, Command, Choice, Option, ParamType, BadParameter, Tuple as click_type_tuple
from click.exceptions import Abort, Exit
from gettext import ngettext
from _collections_abc import dict_values
import os

class BaseWidget(ABC):
    """Provides basic functionalities and initializes the widget.
    Every clickqt widget has to inherit from this class.

    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param parent: The parent BaseWidget of **otype**, defaults to None. Needed for :class:`~clickqt.widgets.basewidget.MultiWidget`-widgets
    :param kwargs: Additionally parameters ('widgetsource', 'com', 'label') needed for 
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type: ClassVar[Type] #: The Qt-type of this widget.

    def __init__(self, otype:ParamType, param:Parameter, parent:"BaseWidget|None"=None, **kwargs):
        assert isinstance(otype, ParamType)
        assert isinstance(param, Parameter)
        self.type:ParamType = otype
        self.param:Parameter = param
        self.parent_widget:BaseWidget|None = parent
        self.click_command:Command = kwargs.get("com")
        self.widget_name = param.name
        self.container = QWidget()
        self.layout = QHBoxLayout()
        self.label = QLabel(text=f"{kwargs.get('label', '')}{self.widget_name}: ")
        if isinstance(param, Option):
            self.container.setToolTip(param.help)
        self.widget = self.createWidget()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.widget)
        self.container.setLayout(self.layout)

        self.widget.setObjectName(param.name) # Only change the stylesheet of this widget and not of all (child-)widgets

        assert self.widget is not None, "Widget not initialized"
        assert self.param is not None, "Click param object not provided"
        assert self.click_command is not None, "Click command not provided"
        assert self.type is not None, "Type not provided"

        self.focus_out_validator = clickqt.core.FocusOutValidator(self)
        self.widget.installEventFilter(self.focus_out_validator)
    
    def createWidget(self) -> QWidget:
        """Creates the widget specified in :attr:`~clickqt.widgets.basewidget.BaseWidget.widget_type` and returns it."""

        return self.widget_type()

    @abstractmethod
    def setValue(self, value:Any):
        """Sets the value of the widget.
        
        :param value: The new value that should be stored in widget
        :raises click.BadParameter: **value** could not be converted into the corresponding click.ParamType
        """

    def isEmpty(self) -> bool:
        """Checks whether the widget is empty. This can be the case for string-based widgets or the 
        multiple choice-widget (:class:`~clickqt.widgets.combobox.CheckableComboBox`).\n
        Subclasses may need to override this method.

        :return: False
        """
        return False

    def getValue(self) -> tuple[Any, ClickQtError]:
        """Validates the value of the widget and returns the result.

        :return: Valid: (widget value or the value of a callback, :class:`~clickqt.core.error.ClickQtError.ErrorType.NO_ERROR`)\n
                 Invalid: (None, :class:`~clickqt.core.error.ClickQtError.ErrorType.CONVERTING_ERROR` or 
                 :class:`~clickqt.core.error.ClickQtError.ErrorType.PROCESSING_VALUE_ERROR`)
        """
        value: Any = None

        try: # Try to convert the provided value into the corresponding click object type
            default = BaseWidget.getParamDefault(self.param, None)
            # if statement is obtained by creating the corresponding truth table
            if self.param.multiple or \
            (not isinstance(self.type, click_type_tuple) and self.param.nargs != 1):
                value_missing = False
                widget_values: list = self.getWidgetValue()

                if len(widget_values) == 0: # Checkable combobox
                    if self.param.required and default is None:
                        self.handleValid(False)
                        return (None, ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR, self.widget_name, self.param.param_type_name))
                    elif default is not None:
                        self.setValue(default)
                        widget_values = self.getWidgetValue()
                    else: # param is not required and there is no default -> value is None
                        value_missing = True # But callback should be considered
                
                if not value_missing:
                    value = []
                    for i, v in enumerate(widget_values): # v is not a BaseWidget, but a primitive type
                        if str(v) == "": # Empty widget (only possible for string based widgets)
                            if self.param.required and default is None:
                                self.handleValid(False)
                                return (None, ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR, self.widget_name, self.param.param_type_name))
                            elif default is not None and i < len(default): # Overwrite the empty widget with the default value and execute with this (new) value
                                values = self.getWidgetValue()
                                values[i] = default[i] # Only overwrite the empty widget, not all
                                self.setValue(values)
                                v = default[i]
                            else: # param is not required, widget is empty and there is no default (click equivalent: option not provided in click command cmd)
                                value = None
                                break
                        
                        value.append(self.type.convert(value=v, param=self.param, ctx=Context(self.click_command))) 
            else:
                value_missing = False
                if self.isEmpty():
                    if self.param.required and default is None:
                        self.handleValid(False)
                        return (None, ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR, self.widget_name, self.param.param_type_name))
                    elif default is not None:
                        self.setValue(default)
                    else:
                        value_missing = True # -> value is None

                if not value_missing:
                    value = self.type.convert(value=self.getWidgetValue(), param=self.param, ctx=Context(self.click_command))
        except Exception as e:
            self.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.CONVERTING_ERROR, self.widget_name, e))

        return self.handleCallback(value)
    
    def handleCallback(self, value:Any) -> tuple[Any, ClickQtError]:
        """Validates **value** in the user-defined callback (if provided) and returns the result.
         
        :param value: The value that should be validated in the callback

        :return: Valid: (**value** or the value of a callback, :class:`~clickqt.core.error.ClickQtError.ErrorType.NO_ERROR`)\n
                 Invalid: (None, :class:`~clickqt.core.error.ClickQtError.ErrorType.ABORTED_ERROR` or 
                 :class:`~clickqt.core.error.ClickQtError.ErrorType.EXIT_ERROR` or :class:`~clickqt.core.error.ClickQtError.ErrorType.PROCESSING_VALUE_ERROR`)
        """

        try: # Consider callbacks 
            ret_val = (self.param.process_value(Context(self.click_command), value), ClickQtError())
            self.handleValid(True)
            return ret_val
        except Abort as e:
            return (None, ClickQtError(ClickQtError.ErrorType.ABORTED_ERROR))
        except Exit as e:
            return (None, ClickQtError(ClickQtError.ErrorType.EXIT_ERROR))
        except Exception as e:
            self.handleValid(False)
            return (None, ClickQtError(ClickQtError.ErrorType.PROCESSING_VALUE_ERROR, self.widget_name, e))

    @abstractmethod
    def getWidgetValue(self) -> Any:
        """Returns the value of the widget without any checks."""
    
    def handleValid(self, valid: bool):
        """Changes the border of the widget dependent on **valid**. If **valid** == False, the border will be colored red, otherwise black.
        
        :param valid: Specifies whether there was no error when validating the widget

        """

        if not valid:
            self.widget.setStyleSheet(f"QWidget#{self.widget.objectName()}{{ border: 1px solid red }}")
        else:
            self.widget.setStyleSheet(f"QWidget#{self.widget.objectName()}{{ }}")
    
    @staticmethod
    def getParamDefault(param:Parameter, alternative=None):
        """Returns the default value of **param**. If there is no default value, **alternative** will be returned."""

        # TODO: Replace with param.get_default(ctx=click.Context(command), call=True)
        if param.default is None:
            return alternative
        if callable(param.default):
            return param.default()
        return param.default


class NumericField(BaseWidget):
    def setValue(self, value: Any):
        self.widget.setValue(self.type.convert(value=str(value), param=self.click_command, ctx=Context(self.click_command)))

    def setMinimum(self, value: int|float):
        self.widget.setMinimum(value)

    def setMaximum(self, value: int|float):
        self.widget.setMaximum(value)
    
    def getWidgetValue(self) -> int|float:
        return self.widget.value()
    

class ComboBoxBase(BaseWidget):
    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert isinstance(otype, Choice), f"'otype' must be of type '{Choice}', but is '{type(otype)}'."

        self.addItems(otype.choices)

    @abstractmethod
    def addItems(self, items:list[str]):
        """
            Adds items to the combobox
        """

class MultiWidget(BaseWidget):
    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)
        
        self.children:list[BaseWidget]|dict_values[BaseWidget] = []

    def init(self):
        if self.parent_widget is None:
            # Consider envvar
            if (envvar_values := self.param.resolve_envvar_value(Context(self.click_command))) is not None:
                # self.type.split_envvar_value(envvar_values) does not work because clicks "self.envvar_list_splitter" is not set corrently
                self.setValue(envvar_values.split(os.path.pathsep))
            elif (default := BaseWidget.getParamDefault(self.param, None)) is not None: # Consider default value
                self.setValue(default)

    def setValue(self, value):
        if len(value) != self.param.nargs:
            raise BadParameter(ngettext("Takes {nargs} values but 1 was given.", "Takes {nargs} values but {len} were given.",len(value))
                               .format(nargs=self.param.nargs, len=len(value)),
                               ctx=Context(self.click_command),
                               param=self.param)
        
        for i,c in enumerate(self.children):
            c.setValue(value[i])

    def handleValid(self, valid: bool):
        for c in self.children:
            c.handleValid(valid) # Recursive

    def isEmpty(self) -> bool:
        if len(self.children) == 0:
            return True

        for c in self.children:
            if c.isEmpty():
                return True
        
        return False
    
    def getWidgetValue(self) -> list[Any]:
        return [c.getWidgetValue() for c in self.children]