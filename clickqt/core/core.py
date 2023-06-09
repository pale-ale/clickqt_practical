import click
import inspect
from clickqt.widgets.multivaluewidget import MultiValueWidget
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTabWidget, QMessageBox, QPlainTextEdit
from PySide6.QtGui import QColor
from clickqt.widgets.checkbox import CheckBox
from clickqt.widgets.textfield import TextField
from clickqt.widgets.passwordfield import PasswordField
from clickqt.widgets.numericfields import IntField, RealField
from clickqt.widgets.combobox import ComboBox, CheckableComboBox
from clickqt.widgets.datetimeedit import DateTimeEdit
from clickqt.widgets.tuplewidget import TupleWidget
from clickqt.widgets.filepathfield import FilePathField
from clickqt.widgets.filefield import FileFild
from clickqt.widgets.nvaluewidget import NValueWidget
from clickqt.core.error import ClickQtError
from clickqt.core.output import OutputStream, TerminalOutput
from typing import Dict, Callable, List, Any, Tuple
import sys

def qtgui_from_click(cmd):
    # Groups-Command-name concatinated with ":" to command-option-names to callables + expose value
    widget_registry: Dict[str, Dict[str, Tuple[Callable, bool]]] = {}

    def parameter_to_widget(command: click.Command, groups_command_name:str, param: click.core.Parameter) -> QWidget:
        if param.name:
            if param.nargs == 1 or isinstance(param.type, click.types.Tuple):
                widget = create_widget(param.type, param.to_info_dict(), widgetsource=create_widget, com=command, o=param)
            else:
                widget = create_widget_mult(param.type, param.nargs, param.to_info_dict(), com=command, o=param)
                
            widget_registry[groups_command_name][param.name] = (lambda: widget.getValue(), param.expose_value)

            return widget.container
        else:
            raise SyntaxError("No parameter name specified")

    def create_widget(otype, *args, **kwargs):
        typedict = {
            click.types.BoolParamType: CheckBox,
            click.types.IntParamType: IntField,
            click.types.FloatParamType: RealField,
            click.types.StringParamType: PasswordField if hasattr(kwargs.get("o"), "hide_input") and kwargs["o"].hide_input else TextField,
            click.types.DateTime: DateTimeEdit,
            click.types.Tuple: TupleWidget,
            click.types.Choice: ComboBox,
            click.types.Path: FilePathField,
            click.types.File: FileFild,
        }
        
        def get_multiarg_version(otype):
            if isinstance(otype, click.types.Choice):
                return CheckableComboBox
            return NValueWidget
        
        if hasattr(kwargs.get("o"), "multiple") and kwargs["o"].multiple:
            return get_multiarg_version(otype)(*args, **kwargs)

        for t,widgetclass in typedict.items():
            if isinstance(otype, t):
                return widgetclass(*args, **kwargs)
        raise NotImplementedError(otype)    
          
    def create_widget_mult(otype, onargs, *args, **kwargs):
        return MultiValueWidget(*args, otype, onargs, **kwargs)
    
    def concat(a: str, b: str) -> str:
        return a + ":" + b
    
    def parse_cmd_group(cmdgroup: click.Group, group_names: str) -> QTabWidget:
        group_tab_widget = QTabWidget()
        for group_name, group_cmd in cmdgroup.commands.items():
            if isinstance(group_cmd, click.Group):
                nested_group_tab_widget = parse_cmd_group(group_cmd, concat(group_names, group_name) if group_names else group_name)
                group_tab_widget.addTab(nested_group_tab_widget, group_name)
            else:
                cmd_tab_widget = QWidget()
                cmd_tab_layout = QVBoxLayout()
                cmd_tab_widget.setLayout(cmd_tab_layout)
                cmd_tab_layout.addWidget(parse_cmd(group_cmd, concat(group_names, group_cmd.name)))
                group_tab_widget.addTab(cmd_tab_widget, group_name)
        return group_tab_widget

    
    def parse_cmd(cmd: click.Command, groups_command_name: str):
        cmdbox = QWidget()
        cmd_elements = QVBoxLayout()
        cmdbox.setLayout(cmd_elements)

        if widget_registry.get(groups_command_name) is None:
            widget_registry[groups_command_name] = {}
        else:
            raise RuntimeError(f"Not a unique group_command_name_concat ({groups_command_name})")    

        for param in cmd.params:
            if isinstance(param, click.core.Parameter):
                # Yes-Parameter
                if hasattr(param, "is_flag") and param.is_flag and hasattr(param, "prompt") and param.prompt:
                    prompt = str(param.prompt)
                    ret = lambda: (True, ClickQtError()) if QMessageBox(QMessageBox.Information, "Confirmation", prompt, \
                                                                        QMessageBox.Yes|QMessageBox.No).exec() == QMessageBox.Yes \
                                                        else (False, ClickQtError(ClickQtError.ErrorType.ABORTED_ERROR))  
                    widget_registry[groups_command_name][param.name] = (lambda: (ret, ClickQtError()), param.expose_value)
                else:  
                    cmd_elements.addWidget(parameter_to_widget(cmd, groups_command_name, param))
        return cmdbox
    
    def check_error(err: ClickQtError) -> bool:
        if err.type != ClickQtError.ErrorType.NO_ERROR:
            if err.type != ClickQtError.ErrorType.ABORTED_ERROR:
                print(err.message(), file=sys.stderr)
            return True
        return False
    
    def check_list(widget_value: List[Any]) -> Tuple[List[Any], ClickQtError]:
        tupleList = []
        for v, err in widget_value:
            if err.type != ClickQtError.ErrorType.NO_ERROR:
                return [], err
            if isinstance(v, list): # and len(v) and isinstance(v[0], tuple):
                t, err = check_list(v)
                if err.type != ClickQtError.ErrorType.NO_ERROR:
                    return [], err
                tupleList.append(t)
            else:
                tupleList.append(v) 
        return tupleList, ClickQtError()

    app = QApplication([])
    app.setApplicationName("GUI for CLI")
    main_tab_widget = QTabWidget()
    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)
    layout.addWidget(main_tab_widget)

    app.setStyleSheet("""QToolTip { 
                           background-color: #182035; 
                           color: white; 
                           border: white solid 1px
                           }""")
    
    if isinstance(cmd, click.Group):
        main_tab_widget.addTab(parse_cmd_group(cmd, cmd.name), cmd.name)
    else:
        standalone_group = QWidget()
        standalone_group_layout = QVBoxLayout()
        standalone_group.setLayout(standalone_group_layout)
        standalone_group_layout.addWidget(parse_cmd(cmd, cmd.name))
        main_tab_widget.addTab(standalone_group, cmd.name if hasattr(cmd, "name") else "Main")
        
    run_button = QPushButton("&Run")  # Shortcut Alt+R

    def current_command(tab_widget: QTabWidget, group: click.Group|click.Command) -> tuple[click.Command, str]:
        """
            Returns the command of the selected tab and a string containing all group names and 
            the seleceted command name
        """
        if isinstance(group, click.Group):
            command = group.get_command(ctx=None, cmd_name=tab_widget.tabText(tab_widget.currentIndex()))
            if isinstance(tab_widget.currentWidget(), QTabWidget):
                g, n = current_command(tab_widget.currentWidget(), command)
                return (command.get_command(ctx=None, cmd_name=g.name), concat(group.name, n))
            return (command, concat(group.name, command.name))
        else:
            return (group, group.name) # =command

    def run():
        selected_command, selected_command_name = current_command(main_tab_widget.currentWidget(), cmd) 

        args: List|Dict[str, Any] = None
        has_error = False
        unused_options: List[Callable] = [] # parameters with expose_value==False

        if inspect.getfullargspec(selected_command.callback).varkw:
            args = {}
        else:
            args = []

        def append(option_name: str, value: Any):
            if isinstance(args, list):
                args.append(value)
            else:
                args[option_name] = value

        # Check all values for errors
        for option_name, (value_callback, expose) in widget_registry[selected_command_name].items():
            if expose:
                widget_value, err = value_callback()   
                if check_error(err):
                    has_error = True
                elif isinstance(widget_value, list) and len(widget_value) and isinstance(widget_value[0], tuple):
                    val, err = check_list(widget_value)
                    if check_error(err):
                        has_error = True
                    append(option_name, val)
                else:
                    append(option_name, widget_value)
            else: # Verify it when all options are valid
                unused_options.append(value_callback)

        if has_error: 
            return

        # Replace the callables with their values and check for errors
        if isinstance(args, list):
            for i in range(len(args)):
                if callable(args[i]):
                    args[i], err = args[i]()
                    if check_error(err):
                        has_error = True
        else:
            for option_name, value in args.items():
                if callable(value):
                    args[option_name], err = value()
                    if check_error(err):
                        has_error = True

        if has_error:
            return

        # Parameters with expose_value==False
        for value_callback in unused_options:
            widget_value, err = value_callback()
            if check_error(err):
                has_error = True 
            if callable(widget_value):
                _, err = widget_value()  
                if check_error(err):
                    has_error = True  
             
        if has_error:
            return
        
        if isinstance(args, list):
            selected_command.callback(*args)
        else:
            selected_command.callback(**args)

                
    run_button.clicked.connect(run)
    layout.addWidget(run_button)

    terminal_output = TerminalOutput()
    terminal_output.setReadOnly(True)
    terminal_output.setToolTip("Terminal output")
    layout.addWidget(terminal_output)
    sys.stdout = OutputStream(terminal_output)
    sys.stderr = OutputStream(terminal_output, QColor("red"))

    def run_app():
        window.show()
        app.exec()

    return run_app
