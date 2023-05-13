import click
import inspect
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, \
    QLineEdit, QGroupBox, QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QFormLayout
from clickqt.checkbox import CheckBox
from clickqt.textfield import TextField
from clickqt.numericfields import IntField, RealField
from clickqt.combobox import ComboBox, CheckableComboBox

from typing import Dict, Callable

def qtgui_from_click(cmd):
    widget_registry: Dict[str, Callable] = {}

    def parameter_to_widget(o):
        if o.name:
            widget = None

            match o.type:
                case click.types.BoolParamType():
                    widget = CheckBox(options=o.to_info_dict())
                case click.types.StringParamType():
                    widget = TextField(options=o.to_info_dict(), hide_input=o.hide_input if hasattr(o, "hide_input") else False) 
                case click.types.IntRange()|click.types.IntParamType(): 
                    widget = IntField(options=o.to_info_dict())
                case click.types.FloatRange():
                    widget = RealField(options=o.to_info_dict())
                case click.types.Choice():
                    if not o.multiple:
                        widget = ComboBox(options=o.to_info_dict())
                    else:
                        widget = CheckableComboBox(options=o.to_info_dict())
                case _:
                    raise NotImplementedError(o.type)
            

            assert widget is not None, "Widget not initialized"
            assert widget.widget is not None, "Qt-Widget not initialized"
            
            widget_registry[o.name] = lambda: widget.getValue()

            return widget.container
        else:
            raise SyntaxError("No parameter name specified")

    def parse_cmd_group(cmdgroup: click.Group) -> list[QGroupBox]:
        groupbox = QGroupBox(cmdgroup.name)
        group_elements = QVBoxLayout()
        groupbox.setLayout(group_elements)
        for cmd in cmdgroup.commands.values():
            cmdbox = QGroupBox(cmd.name)
            cmd_elements = QVBoxLayout()
            cmdbox.setLayout(cmd_elements)
            for param in cmd.params:
                if isinstance(param, (click.core.Argument, click.core.Option)):
                    cmd_elements.addWidget(parameter_to_widget(param))
            group_elements.addWidget(cmdbox)
        return groupbox

    app = QApplication([])
    app.setApplicationName("GUI for CLI")
    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)

    app.setStyleSheet("""QToolTip { 
                           background-color: #182035; 
                           color: white; 
                           border: white solid 1px
                           }""")
    layout.addWidget(parse_cmd_group(cmd))

    run_button = QPushButton("&Run")  # Shortcut Alt+R

    def run():
        if isinstance(cmd, click.Group):
            for subcmd in cmd.commands.values():
                subcmd.callback(
                    *tuple(widget_registry[a]() for a in inspect.getfullargspec(subcmd.callback).args))
                
        app.exit()

    run_button.clicked.connect(run)

    layout.addWidget(run_button)

    def run_app():
        window.show()
        app.exec()

    return run_app
