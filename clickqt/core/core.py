import click
import inspect
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGroupBox, QTabWidget, QMessageBox
from clickqt.widgets.checkbox import CheckBox
from clickqt.widgets.textfield import TextField
from clickqt.widgets.passwordfield import PasswordField
from clickqt.widgets.numericfields import IntField, RealField
from clickqt.widgets.combobox import ComboBox, CheckableComboBox
from clickqt.widgets.datetimeedit import DateTimeEdit
from clickqt.widgets.tuplewidget import TupleWidget
from clickqt.core.error import ClickQtError

from typing import Dict, Callable, List, Any, Tuple

def qtgui_from_click(cmd):
    widget_registry: Dict[str, Callable] = {}

    def parameter_to_widget(o):
        if o.name:
            widget = create_widget(o.type, o.to_info_dict(), o=o, widgetsource=create_widget)

            assert widget is not None, "Widget not initialized"
            assert widget.widget is not None, "Qt-Widget not initialized"
            
            widget_registry[o.name] = lambda: widget.getValue()

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
            click.types.Choice: CheckableComboBox if hasattr(kwargs.get("o"), "multiple") and kwargs["o"].multiple else ComboBox 
        }
        for t,widgetclass in typedict.items():
            if isinstance(otype, t):
                return widgetclass(*args, **kwargs)
        raise NotImplementedError(otype)
        
    def parse_cmd_group(cmdgroup: click.Group) -> list[QGroupBox]:
        groupwidget = QWidget()
        group_elements = QVBoxLayout()
        groupwidget.setLayout(group_elements)
        for cmd in cmdgroup.commands.values():
            group_elements.addWidget(parse_cmd(cmd))
        return groupwidget
    
    def parse_cmd(cmd: click.Command):
        cmdbox = QGroupBox(cmd.name)
        cmd_elements = QVBoxLayout()
        cmdbox.setLayout(cmd_elements)
        for param in cmd.params:
            if isinstance(param, (click.core.Argument, click.core.Option)):
                # Yes-Parameter
                if hasattr(param, "is_flag") and param.is_flag and hasattr(param, "prompt") and param.prompt:
                    qm = QMessageBox(QMessageBox.Information, "Confirmation", str(param.prompt), QMessageBox.Yes|QMessageBox.No)
                    widget_registry[param.name] = lambda: (True, ClickQtError.NO_ERROR) if qm.exec() == QMessageBox.Yes else \
                                                            (False, ClickQtError.ABORDED_ERROR)
                else:    
                    cmd_elements.addWidget(parameter_to_widget(param))
        return cmdbox
    
    def check_error(err: ClickQtError) -> bool:
        if err != ClickQtError.NO_ERROR:
            if err != ClickQtError.ABORDED_ERROR:
                QMessageBox(QMessageBox.Information, "Error", str(err), QMessageBox.Ok).exec()
            return True
        return False
    
    def check_list(widget_value: List[Any]) -> Tuple[List[Any], ClickQtError]:
        tupleList = []
        for v, err in widget_value:
            if err != ClickQtError.NO_ERROR:
                return [], err
            if isinstance(v, list): # and len(v) and isinstance(v[0], tuple):
                t, err = check_list(v)
                if err != ClickQtError.NO_ERROR:
                    return [], err
                tupleList.append(t)
            else:
                tupleList.append(v) 
        return tupleList, ClickQtError.NO_ERROR

    app = QApplication([])
    app.setApplicationName("GUI for CLI")
    tab_widget = QTabWidget()
    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)
    layout.addWidget(tab_widget)
    standalone_group = QWidget()
    standalone_group_layout = QVBoxLayout()
    standalone_group.setLayout(standalone_group_layout)
    tab_widget.addTab(standalone_group, "(No Group)")

    app.setStyleSheet("""QToolTip { 
                           background-color: #182035; 
                           color: white; 
                           border: white solid 1px
                           }""")
    
    if isinstance(cmd, click.Group):
        tab_widget.addTab(parse_cmd_group(cmd), cmd.name)
    else:
        standalone_group_layout.addWidget(parse_cmd(cmd))
        
    run_button = QPushButton("&Run")  # Shortcut Alt+R

    def run():
        if isinstance(cmd, click.Group):
            # TODO: keep both
            for subcmd in cmd.commands.values():
                args = []
                for a in inspect.getfullargspec(subcmd.callback).args:
                    widget_value, err = widget_registry[a]()
                    if check_error(err):
                        return
                    elif isinstance(widget_value, list) and len(widget_value) and isinstance(widget_value[0], tuple):
                        val, err = check_list(widget_value)
                        if check_error(err):
                            return
                        args.append(val)
                    else:
                        args.append(widget_value)
                subcmd.callback(*args)
                
    run_button.clicked.connect(run)

    layout.addWidget(run_button)

    def run_app():
        window.show()
        app.exec()

    return run_app
