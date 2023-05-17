import click
import inspect
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGroupBox, QTabWidget
from clickqt.checkbox import CheckBox
from clickqt.textfield import TextField
from clickqt.numericfields import IntField, RealField
from clickqt.combobox import ComboBox, CheckableComboBox
from clickqt.datetimeedit import DateTimeEdit
from clickqt.tuplewidget import TupleWidget

from typing import Dict, Callable

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
            click.types.StringParamType: TextField,
            click.types.DateTime: DateTimeEdit,
            click.types.Tuple: TupleWidget,
            click.types.Choice: CheckableComboBox if kwargs.get("o") is not None and kwargs["o"].multiple else ComboBox 
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
                cmd_elements.addWidget(parameter_to_widget(param))
        return cmdbox

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
                    widgetcb = widget_registry[a]
                    if isinstance(widgetcb, list):
                        args.append((a2() for a2 in widgetcb))
                        continue
                    args.append(widgetcb())
                subcmd.callback(*args)
                
    run_button.clicked.connect(run)

    layout.addWidget(run_button)

    def run_app():
        window.show()
        app.exec()

    return run_app
