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
from clickqt.widgets.confirmationwidget import ConfirmationWidget
from clickqt.core.error import ClickQtError
from clickqt.core.output import OutputStream, TerminalOutput
from typing import Dict, Callable, List, Any, Tuple
import sys
import re
from functools import reduce

def qtgui_from_click(cmd):
    # Groups-Command-name concatinated with ":" to command-option-names to callables
    widget_registry: Dict[str, Dict[str, Callable[[], tuple[Any, ClickQtError]]]] = {}
    command_param_registry: Dict[str, Dict[str, Tuple[int, Callable]]] = {}

    def parameter_to_widget(command: click.Command, groups_command_name:str, param: click.Parameter) -> QWidget:
        if param.name:
            widget = create_widget(param.type, param, widgetsource=create_widget, com=command)                
            widget_registry[groups_command_name][param.name] = lambda: widget.getValue()
            command_param_registry[groups_command_name][param.name] = (param.nargs, type(param.type).__name__)
            return widget.container
        else:
            raise SyntaxError("No parameter name specified")

    def create_widget(otype:click.ParamType, param:click.Parameter, *args, **kwargs):
        typedict = {
            click.types.BoolParamType: CheckBox,
            click.types.IntParamType: IntField,
            click.types.FloatParamType: RealField,
            click.types.StringParamType: PasswordField if hasattr(param, "hide_input") and param.hide_input else TextField,
            click.types.DateTime: DateTimeEdit,
            click.types.Tuple: TupleWidget,
            click.types.Choice: ComboBox,
            click.types.Path: FilePathField,
            click.types.File: FileFild,
        }

        def get_multiarg_version(otype:click.ParamType):
            if isinstance(otype, click.types.Choice):
                return CheckableComboBox
            return NValueWidget
        
        if hasattr(param, "confirmation_prompt") and param.confirmation_prompt:
            return ConfirmationWidget(param, *args, **kwargs)
        if param.multiple:
            return get_multiarg_version(otype)(param, *args, **kwargs)
        if param.nargs > 1:
            if isinstance(otype, click.types.Tuple):
                return TupleWidget(param, *args, **kwargs)
            return MultiValueWidget(param, *args, **kwargs)

        for t,widgetclass in typedict.items():
            if isinstance(otype, t):
                return widgetclass(param, *args, **kwargs)
        raise NotImplementedError(otype)    

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
        if command_param_registry.get(groups_command_name) is None:
            command_param_registry[groups_command_name] = {}
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
                    widget_registry[groups_command_name][param.name] = lambda: (ret, ClickQtError())
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
        main_tab_widget.addTab(standalone_group, cmd.name)
        
    run_button = QPushButton("&Run")  # Shortcut Alt+R

    def current_command_hierarchy(tab_widget: QTabWidget, group: click.Group|click.Command) -> list[click.Group|click.Command]:
        """
            Returns the hierarchy of the command of the selected tab
        """
        if isinstance(group, click.Group):
            command = group.get_command(ctx=None, cmd_name=tab_widget.tabText(tab_widget.currentIndex()))
            if isinstance(tab_widget.currentWidget(), QTabWidget):
                return [group] + current_command_hierarchy(tab_widget.currentWidget(), command)
            return [group, command]
        else:
            return [group]

        
    def get_params(selected_command_name:str, args):
        params = [k for k, v in widget_registry[selected_command_name].items()]
        if "yes" in params: 
            params.remove("yes")
        command_help = command_param_registry.get(selected_command_name)
        command_help_array = list(command_help.values())
        for i, param in enumerate(params):
            params[i] = "--" + param + f" {command_help_array[i]}: " +  f"{args[param]}"
        return params

                
    def function_call_formatter(hierarchy_selected_command_name:str, selected_command_name:str, args):
        params = get_params(hierarchy_selected_command_name, args)
        message = f"{selected_command_name} \n"
        parameter_message =  f"Current Command parameters: \n" + "\n".join(params)
        return message + parameter_message
    
    def clean_command_string(word, text):
        pattern = r'\b{}\b|[():;]'.format(re.escape(word))  # Create a regex pattern for the word and symbols
        replaced_text = re.sub(pattern, '', text)  # Remove the word and symbols from the text
        return replaced_text
    
    def command_to_string(hierarchy_selected_command_name: str, selected_command, args):
        """ 
            TODO: Write command string such that it can match the exact terminal call. 
        """
        parameter_strings = [k for k, v in widget_registry[hierarchy_selected_command_name].items()]
        parameter_strings = [param for param in parameter_strings if param != 'yes']
        parameter_list = [param for param in selected_command.params if param.name != 'yes']
        for i, param in enumerate(parameter_list):
            if isinstance(param, click.core.Argument):
                """ This is the special case for the arguments. """
                parameter_strings[i] = f"{args[param.name]}"
            if isinstance(param, click.core.Option):
                if param.multiple:
                    num_calls = len(args[param.name])
                    for j in range(num_calls):
                        temp = "--" + param.name + " " + str(args[param.name][j])
                        if len(parameter_strings[i]) == 0:
                            parameter_strings[i] = temp
                        parameter_strings[i] = parameter_strings[i] + temp
                elif isinstance(param.type, click.types.Tuple):
                    temp = "--" + param.name + " " + str(args[param.name])
                    parameter_strings[i] = temp
                else:
                    parameter_strings[i] = "--" + param.name + " " + str(args[param.name])
        for i in range(len(parameter_strings)):
            temp = parameter_strings[i]
            hierarchy_selected_command_name = hierarchy_selected_command_name + " " + temp
            
        hierarchy_selected_command_name = clean_command_string(cmd.name, hierarchy_selected_command_name)
        return hierarchy_selected_command_name 

    def run():
        hierarchy_selected_command = current_command_hierarchy(main_tab_widget.currentWidget(), cmd) 
        selected_command = hierarchy_selected_command[-1]
        #parent_group_command = hierarchy_selected_command[-2] if len(hierarchy_selected_command) >= 2 else None
        hierarchy_selected_command_name = reduce(concat, [g.name for g in hierarchy_selected_command])

        args: Dict[str, Any] = {}
        has_error = False
        unused_options: List[Callable] = [] # parameters with expose_value==False

        # Check all values for errors
        for option_name, value_callback in widget_registry[hierarchy_selected_command_name].items():
            param: click.Parameter = next((x for x in selected_command.params if x.name == option_name))
            if param.expose_value:
                widget_value, err = value_callback()   
                if check_error(err):
                    has_error = True
                elif isinstance(widget_value, list) and len(widget_value) and isinstance(widget_value[0], tuple):
                    widget_value, err = check_list(widget_value)
                    if check_error(err):
                        has_error = True

                args[option_name] = widget_value
            else: # Verify it when all options are valid
                unused_options.append(value_callback)

        if has_error: 
            return

        # Replace the callables with their values and check for errors
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

        print(command_to_string(hierarchy_selected_command_name, selected_command, args))
        print(f"Current Command: {function_call_formatter(hierarchy_selected_command_name, selected_command.name, args)} \n" + f"Output:")
        
        if inspect.getfullargspec(selected_command.callback).varkw:
            selected_command.callback(**args)
        else:
            selected_command.callback(*args.values())

                
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
