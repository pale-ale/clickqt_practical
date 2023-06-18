import click
import inspect
from clickqt.core.gui import GUI
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMessageBox
from clickqt.core.error import ClickQtError
from clickqt.widgets.base_widget import BaseWidget
from typing import Dict, Callable, List, Any, Tuple, Union
import sys
from functools import reduce

class Control:
    def __init__(self, cmd:click.Group|click.Command):
        self.gui = GUI()
        self.cmd = cmd

        # Groups-Command-name concatinated with ":" to command-option-names to BaseWidget or Callable
        self.widget_registry: Dict[str, Dict[str, Union[BaseWidget, Callable[[], Tuple[Any, ClickQtError]]]]] = {}
        self.command_registry: Dict[str, Dict[str, Tuple[int, Callable]]] = {}

        # Add all widgets
        if isinstance(cmd, click.Group):
            self.gui.main_tab.addTab(self.parse_cmd_group(cmd, cmd.name), cmd.name)
        else:
            standalone_group = QWidget()
            standalone_group.setLayout(QVBoxLayout())
            standalone_group.layout().addWidget(self.parse_cmd(cmd, cmd.name))
            self.gui.main_tab.addTab(standalone_group, cmd.name)

        # Connect GUI Run-Button with run method
        self.gui.run_button.clicked.connect(self.run)

    def __call__(self):
        self.gui()
    
    def parameter_to_widget(self, command: click.Command, groups_command_name:str, param: click.Parameter) -> QWidget:
        if param.name:
            assert self.widget_registry[groups_command_name].get(param.name) is None

            widget = self.gui.create_widget(param.type, param, widgetsource=self.gui.create_widget, com=command)                
            self.widget_registry[groups_command_name][param.name] = widget
            self.command_registry[groups_command_name][param.name] = (param.nargs, type(param.type).__name__)
            
            return widget.container
        else:
            raise SyntaxError("No parameter name specified")

    def concat(self, a: str, b: str) -> str:
        return a + ":" + b
    
    def parse_cmd_group(self, cmdgroup: click.Group, group_names: str) -> QTabWidget:
        group_tab_widget = QTabWidget()
        for group_name, group_cmd in cmdgroup.commands.items():
            if isinstance(group_cmd, click.Group):
                nested_group_tab_widget = self.parse_cmd_group(group_cmd, self.concat(group_names, group_name) if group_names else group_name)
                group_tab_widget.addTab(nested_group_tab_widget, group_name)
            else:
                cmd_tab_widget = QWidget()
                cmd_tab_widget.setLayout(QVBoxLayout())
                cmd_tab_widget.layout().addWidget(self.parse_cmd(group_cmd, self.concat(group_names, group_cmd.name)))
                group_tab_widget.addTab(cmd_tab_widget, group_name)
        return group_tab_widget

    
    def parse_cmd(self, cmd: click.Command, groups_command_name: str):
        cmdbox = QWidget()
        cmdbox.setLayout(QVBoxLayout())

        if self.widget_registry.get(groups_command_name) is None:
            self.widget_registry[groups_command_name] = {}
        if self.command_registry.get(groups_command_name) is None:
            self.command_registry[groups_command_name] = {}
        else:
            raise RuntimeError(f"Not a unique group_command_name_concat ({groups_command_name})")    

        # parameter name to flag values
        feature_switches:dict[str, list[click.Parameter]] = {}

        for param in cmd.params:
            if isinstance(param, click.core.Parameter):
                # Yes-Parameter
                if hasattr(param, "is_flag") and param.is_flag and hasattr(param, "prompt") and param.prompt:
                    prompt = str(param.prompt)
                    ret = lambda: (True, ClickQtError()) if QMessageBox(QMessageBox.Information, "Confirmation", prompt, \
                                                                        QMessageBox.Yes|QMessageBox.No).exec() == QMessageBox.Yes \
                                                        else (False, ClickQtError(ClickQtError.ErrorType.ABORTED_ERROR))  
                    self.widget_registry[groups_command_name][param.name] = lambda: (ret, ClickQtError())
                elif hasattr(param, "is_flag") and param.is_flag and hasattr(param, "flag_value") and param.flag_value: # clicks feature switches
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

        return cmdbox
    
    def check_error(self, err: ClickQtError) -> bool:
        if err.type != ClickQtError.ErrorType.NO_ERROR:
            print(err.message(), file=sys.stderr)
            return True
        
        return False

    def current_command_hierarchy(self, tab_widget: QTabWidget, group: click.Group|click.Command) -> list[click.Group|click.Command]:
        """
            Returns the hierarchy of the command of the selected tab
        """
        if isinstance(group, click.Group):
            command = group.get_command(ctx=None, cmd_name=tab_widget.tabText(tab_widget.currentIndex()))
            if isinstance(tab_widget.currentWidget(), QTabWidget):
                return [group] + self.current_command_hierarchy(tab_widget.currentWidget(), command)
            return [group, command]
        else:
            return [group]
        
    def get_params(self, selected_command_name:str, args):
        params = [k for k, v in self.widget_registry[selected_command_name].items()]
        if "yes" in params: 
            params.remove("yes")
        command_help = self.command_registry.get(selected_command_name)
        tuples_array = list(command_help.values())
        for i, param in enumerate(params):
            params[i] = "--" + param + f": {tuples_array[i]}: " +  f"{args[param]}"
        return params
                
    def function_call_formatter(self, hierarchy_selected_command_name:str, selected_command_name:str, args):
        params = self.get_params(hierarchy_selected_command_name, args)
        message = f"{selected_command_name} \n"
        parameter_message =  f"Current Command parameters: \n" + "\n".join(params)
        return message + parameter_message

    def run(self):
        hierarchy_selected_command = self.current_command_hierarchy(self.gui.main_tab.currentWidget(), self.cmd) 
        selected_command = hierarchy_selected_command[-1]
        #parent_group_command = hierarchy_selected_command[-2] if len(hierarchy_selected_command) >= 2 else None
        hierarchy_selected_command_name = reduce(self.concat, [g.name for g in hierarchy_selected_command])

        kwargs: Dict[str, Any] = {}
        has_error = False
        unused_options: List[Callable] = [] # parameters with expose_value==False

        # Check all values for errors
        for option_name, widget_or_callable in self.widget_registry[hierarchy_selected_command_name].items():
            param: click.Parameter = next((x for x in selected_command.params if x.name == option_name))
            if param.expose_value:
                widget_value, err = widget_or_callable()   
                has_error |= self.check_error(err)

                kwargs[option_name] = widget_value
            else: # Verify it when all options are valid
                unused_options.append(widget_or_callable)

        if has_error: 
            return

        # Replace the callables with their values and check for errors
        for option_name, value in kwargs.items():
            if callable(value):
                kwargs[option_name], err = value()
                has_error |= self.check_error(err)

        if has_error:
            return

        # Parameters with expose_value==False
        for widget_or_callable in unused_options:
            widget_value, err = widget_or_callable()
            has_error |= self.check_error(err)
            if callable(widget_value):
                _, err = widget_value()  
                has_error |= self.check_error(err)
             
        if has_error:
            return
        
        print(f"Current Command: {self.function_call_formatter(hierarchy_selected_command_name, selected_command.name, kwargs)} \n" + f"Output:")

        if len(callback_args := inspect.getfullargspec(selected_command.callback).args) > 0:
            args: list[Any] = []
            for ca in callback_args: # Bring the args in the correct order
                args.append(kwargs.pop(ca)) # Remove explicitly mentioned args from kwargs dict
            selected_command.callback(*args, **kwargs)
        else:
            selected_command.callback(**kwargs) # Throws an error (click does the same)
