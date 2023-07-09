import click
import inspect
from clickqt.core.gui import GUI
from clickqt.core.commandexecutor import CommandExecutor
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QTabWidget, QScrollArea
from PySide6.QtCore import QThread, QObject, Signal, Slot
from PySide6.QtGui import QPalette
from clickqt.core.error import ClickQtError
from clickqt.widgets.confirmationwidget import ConfirmationWidget
from clickqt.widgets.basewidget import BaseWidget
from typing import Dict, Callable, List, Any, Tuple
import sys
from functools import reduce
import re 
from clickqt.core.utils import *


class Control(QObject):
    requestExecution = Signal(list, click.Context) # Generics do not work here

    def __init__(self, cmd:click.Group|click.Command, is_ep:bool=None, ep_or_eppath:str=None):
        super().__init__()
        """ __init__ function initializing the GUI object and the registries together with the differentiation of a group command and a simple command. """

        self.gui = GUI()
        self.cmd = cmd

        # Create a worker in another thread when the user clicks the run button
        # Don't destroy a thread when no command is running and the user closes the application
        # Otherwise "QThread: Destroyed while thread is still running" would be appear
        self.worker_thread: QThread = None
        self.worker: CommandExecutor = None

        # Connect GUI buttons with slots
        self.gui.run_button.clicked.connect(self.startExecution)
        self.gui.stop_button.clicked.connect(self.stopExecution)

        # Groups-Command-name concatinated with ":" to command-option-names to BaseWidget
        self.widget_registry: Dict[str, Dict[str, BaseWidget]] = {}
        self.command_registry: Dict[str, Dict[str, Tuple[int, Callable]]] = {}
        self.ep_or_path = ep_or_eppath
        self.is_entrypoint = is_ep

        # Add all widgets
        if isinstance(cmd, click.Group):
            child_tabs: QWidget = None
            if len(cmd.params) > 0:
                child_tabs = QWidget()
                child_tabs.setLayout(QVBoxLayout())
                child_tabs.layout().addWidget(self.parse_cmd(cmd, cmd.name)) # Group params
                child_tabs.layout().addWidget(self.parse_cmd_group(cmd, cmd.name)) # Child group/commands params 
            else:
                child_tabs = self.parse_cmd_group(cmd, cmd.name)

            self.gui.main_tab.addTab(child_tabs, cmd.name)
        else:
            self.gui.main_tab.addTab(self.parse_cmd(cmd, cmd.name), cmd.name)

    def __call__(self):
        self.gui()
    
    def parameter_to_widget(self, command: click.Command, groups_command_name:str, param: click.Parameter) -> QWidget:
        assert param.name, "No parameter name specified"
        assert self.widget_registry[groups_command_name].get(param.name) is None
        
        widget = self.gui.create_widget(param.type, param, widgetsource=self.gui.create_widget, com=command)                
        self.widget_registry[groups_command_name][param.name] = widget
        self.command_registry[groups_command_name][param.name] = (param.nargs, type(param.type).__name__)
        
        return widget.container

    def concat(self, a: str, b: str) -> str:
        """ Returns a concatenated string """
        return a + ":" + b
    
    def parse_cmd_group(self, cmdgroup: click.Group, group_names: str) -> QTabWidget:
        """ Function to parse the information of a grouped click command. """
        group_tab_widget = QTabWidget()
        for group_name, group_cmd in cmdgroup.commands.items():
            if isinstance(group_cmd, click.Group):
                child_tabs: QWidget = None
                concat_group_names = self.concat(group_names, group_name) if group_names else group_name
                if len(group_cmd.params) > 0:
                    child_tabs = QWidget()
                    child_tabs.setLayout(QVBoxLayout())
                    child_tabs.layout().addWidget(self.parse_cmd(group_cmd, concat_group_names))
                    child_tabs.layout().addWidget(self.parse_cmd_group(group_cmd, concat_group_names))
                else:
                    child_tabs = self.parse_cmd_group(group_cmd, concat_group_names)

                group_tab_widget.addTab(child_tabs, group_name)
            else:
                group_tab_widget.addTab(self.parse_cmd(group_cmd, self.concat(group_names, group_cmd.name)), group_name)
        
        return group_tab_widget
    
    def parse_cmd(self, cmd: click.Command, groups_command_name: str):
        """ Function to parse the information of a simple command. """
        cmdbox = QWidget()
        cmdbox.setLayout(QVBoxLayout())

        assert self.widget_registry.get(groups_command_name) is None, f"Not a unique group_command_name_concat ({groups_command_name})"

        self.widget_registry[groups_command_name] = {}
        self.command_registry[groups_command_name] = {}
  
        # parameter name to flag values
        feature_switches:dict[str, list[click.Parameter]] = {}

        for param in cmd.params:
            if isinstance(param, click.core.Parameter):
                if hasattr(param, "is_flag") and param.is_flag and \
                    hasattr(param, "flag_value") and isinstance(param.flag_value, str) and param.flag_value: # clicks feature switches
                    if feature_switches.get(param.name) is None:
                        feature_switches[param.name] = []
                    feature_switches[param.name].append(param)
                else:  
                    cmdbox.layout().addWidget(self.parameter_to_widget(cmd, groups_command_name, param))
        
        # Create for every feature switch a ComboBox
        for param_name, switch_names in feature_switches.items():
            choice = click.Option([f"--{param_name}"], type=click.Choice([x.flag_value for x in switch_names]), required=reduce(lambda x,y: x | y.required, switch_names, False))
            default = next((x.flag_value for x in switch_names if x.default), switch_names[0].flag_value) # First param with default==True is the default
            cmdbox.layout().addWidget(self.parameter_to_widget(cmd, groups_command_name, choice))
            self.widget_registry[groups_command_name][param_name].setValue(default)

        cmd_tab_widget = QScrollArea()
        cmd_tab_widget.setFrameShape(QFrame.Shape.NoFrame) # Remove black border
        cmd_tab_widget.setBackgroundRole(QPalette.ColorRole.Light)
        cmd_tab_widget.setWidgetResizable(True) # Widgets should use the whole area
        cmd_tab_widget.setWidget(cmdbox)

        return cmd_tab_widget
    
    def check_error(self, err: ClickQtError) -> bool:
        """ Returns if parameter has Error. """
        if err.type != ClickQtError.ErrorType.NO_ERROR:
            if (message := err.message()): # Don't print on context exit
                print(message, file=sys.stderr)
            return True
        
        return False

    def current_command_hierarchy(self, tab_widget: QTabWidget|QWidget, group: click.Group|click.Command) -> list[click.Group|click.Command]:
        """
            Returns the hierarchy of the command of the selected tab
        """
        if isinstance(group, click.Group):
            if len(group.params) > 0: # Group has params
                tab_widget = tab_widget.findChild(QTabWidget)
            
            command = group.get_command(ctx=None, cmd_name=tab_widget.tabText(tab_widget.currentIndex()))

            return [group] + self.current_command_hierarchy(tab_widget.currentWidget(), command)
        else:
            return [group]
        
    def get_option_names(self,cmd):
        """ Returns an array of all the parameters used for the current command togeter with their properties."""
        option_names = []
        for param in cmd.params:
            if isinstance(param, click.Option):
                long_forms = [opt for opt in param.opts if opt.startswith('--')]
                longest_long_form = max(long_forms, key=len) if long_forms else None
                short_forms = [opt for opt in param.opts if opt.startswith("-")]
                short_forms = max(short_forms, key=len) if short_forms else None
                if longest_long_form:
                    option_names.append((longest_long_form, param.type, param.multiple))
                else: 
                    option_names.append((short_forms, param.type, param.multiple))
            elif isinstance(param, click.Argument):
                option_names.append(("Argument", param.type))
        return option_names
        
    def get_params(self, selected_command_name:str, args):
        """ Returns an array of strings that are used for the output field."""
        params = [k for k, v in self.widget_registry[selected_command_name].items()]
        if "yes" in params: 
            params.remove("yes")
        command_help = self.command_registry.get(selected_command_name)
        tuples_array = list(command_help.values())
        for i, param in enumerate(args):
            params[i] = "--" + param + f": {tuples_array[i]}: " +  f"{args[param]}"
        return params
    
    def clean_command_string(self, word, text):
        """ Returns a string without any special characters using regex."""
        text = re.sub(r'\b{}\b'.format(re.escape(word)), '', text)
        text = re.sub(r'[^a-zA-Z0-9 .-]', ' ', text)
        return text
    
    def command_to_string(self, hierarchy_selected_command_name: str):
        """ Returns the current command name. """
        hierarchy_selected_command_name = self.clean_command_string(self.cmd.name, hierarchy_selected_command_name)
        return hierarchy_selected_command_name
    
    
    def command_to_string_to_copy(self, hierarchy_selected_name:str, selected_command):
        """ Returns a string representing the click command if one actually would actually execute it in the shell"""
        parameter_list = self.get_option_names(selected_command)
        parameter_list = [param for param in parameter_list if param[0] != "--yes"]
        widgets = self.widget_registry[hierarchy_selected_name]
        widget_values = []
        for widget in widgets:
            if type(widget) != ConfirmationWidget and widget != "yes":
                widget_values.append(widgets[widget].getWidgetValue())
        parameter_strings = []
        for i, param in enumerate(parameter_list):
            if param[0] != "Argument":
                if type(widget_values[i]) != list or param[2] != True:
                    widget_value = str(widget_values[i])
                    if not is_file_path(widget_value):
                        parameter_strings.append(parameter_list[i][0] + " " + re.sub(r'[^a-zA-Z0-9 .-]', ' ', widget_value))
                    else: 
                        parameter_strings.append(parameter_list[i][0] + " " + widget_value)
                else:
                    if is_nested_list(widget_values[i]):
                        depth = len(widget_values[i])
                        for j in range(depth):
                            widget_value = str(widget_values[i][j])
                            if not is_file_path(widget_value):
                                parameter_strings.append(parameter_list[i][0] + " " + re.sub(r'[^a-zA-Z0-9 .-]', ' ', widget_value))
                            else:
                                parameter_strings.append(parameter_list[i][0] + " " + widget_value)
                    else:
                        length = len(widget_values[i])
                        for j in range(length):
                            widget_value = str(widget_values[i][j])
                            if not is_file_path(widget_value):
                                parameter_strings.append(parameter_list[i][0] + " " + re.sub(r'[^a-zA-Z0-9 .-]', ' ', widget_value))
                            else:
                                parameter_strings.append(parameter_list[i][0] + " " + widget_value)
            else:
                parameter_strings.append(str(widget_values[i])) 
        message = hierarchy_selected_name + " " + " ".join(parameter_strings)
        message = re.sub(r'\b{}\b'.format(re.escape(self.cmd.name)), '', message)
        message = message.replace(":", " ")
        return message
                        
    def function_call_formatter(self, hierarchy_selected_command_name:str, selected_command_name:str, args):
        params = self.get_params(hierarchy_selected_command_name, args)
        message = f"{selected_command_name} \n"
        parameter_message =  f"Current Command parameters: \n" + "\n".join(params)
        return message + parameter_message
    
    @Slot()
    def stopExecution(self):
        print("Execution stopped!", file=sys.stderr)
        self.worker_thread.terminate()
        self.executionFinished()

    @Slot()
    def executionFinished(self):
        self.worker_thread.deleteLater()
        self.worker.deleteLater()

        self.worker_thread = None
        self.worker = None

        self.gui.run_button.setEnabled(True)
        self.gui.stop_button.setEnabled(False)

    @Slot()
    def startExecution(self):
        hierarchy_selected_command = self.current_command_hierarchy(self.gui.main_tab.currentWidget(), self.cmd)
        
        def run_command(command:click.Command|click.Group, hierarchy_command:str) -> Callable|None:
            kwargs: Dict[str, Any] = {}
            has_error = False
            unused_options: List[BaseWidget] = [] # parameters with expose_value==False

            if self.widget_registry.get(hierarchy_command) is not None: # Groups with no options are not in the dict
                # Check all values for errors
                for option_name, widget in self.widget_registry[hierarchy_command].items():
                    param: click.Parameter = next((x for x in command.params if x.name == option_name))
                    if param.expose_value:
                        widget_value, err = widget.getValue()  
                        has_error |= self.check_error(err)

                        kwargs[option_name] = widget_value
                    else: # Verify it when all options are valid
                        unused_options.append(widget)

                if has_error:
                    return None

                # Replace the callables with their values and check for errors
                for option_name, value in kwargs.items():
                    if callable(value):
                        kwargs[option_name], err = value()
                        has_error |= self.check_error(err)

                if has_error:
                    return None

                # Parameters with expose_value==False
                for widget in unused_options:
                    widget_value, err = widget.getValue()
                    has_error |= self.check_error(err)
                    if callable(widget_value):
                        _, err = widget_value()  
                        has_error |= self.check_error(err)
                    
                if has_error:
                    return None

            if len(callback_args := inspect.getfullargspec(command.callback).args) > 0:
                args: list[Any] = []
                for ca in callback_args: # Bring the args in the correct order
                    args.append(kwargs.pop(ca)) # Remove explicitly mentioned args from kwargs

                if self.is_entrypoint:
                    print(f"For command details, please call '{self.command_to_string(hierarchy_command)} --help'")
                    print(f"{self.ep_or_path} {self.command_to_string_to_copy(hierarchy_command, command)}")
                    print(f"Current Command: {self.function_call_formatter(hierarchy_command, command, kwargs)} \n" + f"Output:")
                    return lambda: command.callback(*args, **kwargs)
                else:
                    print(f"For command details, please call '{self.command_to_string(hierarchy_command)} --help'")
                    print(f"python {self.ep_or_path} {self.command_to_string_to_copy(hierarchy_command, command)}")
                    print(f"Current Command: {self.function_call_formatter(hierarchy_command, command, kwargs)} \n" + f"Output:") 
                    return lambda: command.callback(*args, **kwargs)
            else:
                return lambda: command.callback(**kwargs)
            
        callables:list[Callable] = []
        for i, command in enumerate(hierarchy_selected_command, 1):    
            if (c := run_command(command, reduce(self.concat, [g.name for g in hierarchy_selected_command[:i]]))) is not None:
                callables.append(c)
  
        if len(callables) == len(hierarchy_selected_command):
            self.gui.run_button.setEnabled(False)
            self.gui.stop_button.setEnabled(True)

            self.worker_thread = QThread()
            self.worker_thread.start()
            self.worker = CommandExecutor()
            self.worker.moveToThread(self.worker_thread)
            self.worker.finished.connect(self.worker_thread.quit)
            self.worker.finished.connect(self.executionFinished)
            self.requestExecution.connect(self.worker.run)

            self.requestExecution.emit(callables, click.Context(hierarchy_selected_command[-1]))
        