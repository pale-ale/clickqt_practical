import click
import inspect
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QLineEdit, QGroupBox, QLabel, QComboBox, QSpinBox, QDoubleSpinBox
from clickqt.checkableComboBox import CheckableComboBox

def qtgui_from_click(cmd):
    widget_registry = {}

    def parameter_to_widget(o):
        if o.name:
            param = QWidget()
            hBox = QHBoxLayout()
            widget = None
            param.setLayout(hBox)
            label = QLabel(f"{o.name}: ")
            add_tooltip(label, o)
            hBox.addWidget(label)

            match o.type:
                case click.types.BoolParamType():
                    widget = QCheckBox()
                    if o.default() if callable(o.default) else o.default:
                        widget.setChecked(True)
                    widget_registry[o.name] = lambda: widget.isChecked()
                case click.types.StringParamType():
                    widget = QLineEdit(o.default() if callable(
                        o.default) else o.default)
                    if hasattr(o, "hide_input"):
                        widget.setEchoMode(QLineEdit.EchoMode.Password)
                    widget_registry[o.name] = lambda: widget.text()
                case click.types.IntRange() | click.types.FloatRange():
                    widget = QSpinBox() if isinstance(o.type, click.types.IntRange) else QDoubleSpinBox()
                    #QSpinBox is limited to [-2**31; 2**31-1], but sys.maxsize returns 2**63 - 1
                    widget.setMinimum(o.to_info_dict()["type"]["min"] if o.to_info_dict()["type"]["min"] is not None 
                                      else (-2**31 if isinstance(o.type, click.types.IntRange) 
                                            else -sys.float_info.max))
                    widget.setMaximum(o.to_info_dict()["type"]["max"] or 
                                      (2**31 - 1 if isinstance(o.type, click.types.IntRange) 
                                       else sys.float_info.max) ) 
                    widget.setValue((o.default() if callable(o.default) else o.default) or 0)
                    widget_registry[o.name] = lambda: widget.value()
                case click.types.IntParamType():
                    widget = QLineEdit()
                    widget_registry[o.name] = lambda: widget.text()
                case click.types.Choice():
                    if not o.multiple:
                        widget = QComboBox()
                        widget.addItems(o.to_info_dict()["type"]["choices"])
                        widget_registry[o.name] = lambda: widget.currentText()
                    else:
                        widget = CheckableComboBox()
                        widget.addItems(o.to_info_dict()["type"]["choices"])
                        widget_registry[o.name] = lambda: widget.currentData()
                case _:
                    raise NotImplementedError(o.type)

            assert widget is not None, "Widget not initialized"

            hBox.addWidget(widget)

            return param
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

    def add_tooltip(widget: QWidget, o):
        widget.setToolTip(o.help if hasattr(o, "help")
                          else "No info available.")

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

    run_button.clicked.connect(run)

    layout.addWidget(run_button)

    def run_app():
        window.show()
        app.exec()

    return run_app
