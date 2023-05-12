import click
import inspect
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QLineEdit, QGroupBox, QLabel, QComboBox, QDateTimeEdit, QSpinBox
from clickqt.checkableComboBox import CheckableComboBox
from .postprocessing import PostProcessor

def qtgui_from_click(cmd):
    widget_registry = {}
    postprocessor = PostProcessor()           

    def parameter_to_widget(o:click.Argument|click.Option):
        if o.name:
            param = QWidget()
            hBox = QHBoxLayout()
            param.setLayout(hBox)
            label = QLabel(f"{o.name}: ")
            add_tooltip(label, o)
            hBox.addWidget(label)

            widget = type_to_widget(o.type, o.name)

            assert widget is not None, "Widget not initialized"

            if postprocessor:
                postprocessor.post_process(widget, o)

            hBox.addWidget(widget)

            return param
        else:
            raise SyntaxError("No parameter name specified")
    
    def type_to_widget(otype, oname, hints:list[str] = list()):
        def add_to_registry(widget, oname, func):
            if oname in widget_registry:
                widget_registry[oname].append(func)
            else:
                widget_registry[oname] = func
    
        match otype:
            case click.types.BoolParamType():
                widget = QCheckBox()
                add_to_registry(widget, oname, lambda: widget.isChecked())
            case click.types.StringParamType():
                widget = QLineEdit()
                add_to_registry(widget, oname, lambda: widget.text())
            case click.types.IntRange():
                widget = QSpinBox()
                add_to_registry(widget, oname, lambda:
                    len(widget.text()) if not widget.text().isnumeric() else int(widget.text()))
            case click.types.IntParamType():
                widget = QSpinBox()
                add_to_registry(widget, oname, lambda: widget.value())
            case click.types.Choice():
                widget = CheckableComboBox() if "multiple" in hints else QComboBox()
                add_to_registry(widget, oname, lambda: widget.currentText())
            case click.types.DateTime():
                widget = QDateTimeEdit()
                add_to_registry(widget, oname, lambda: widget.date())
            case click.types.Tuple():
                widget = QGroupBox()
                hBox = QHBoxLayout()
                widget.setLayout(hBox)
                widget_registry[oname] = []
                for t in otype.types:
                    hBox.addWidget(type_to_widget(t, oname, hints))
            case _:
                raise NotImplementedError(otype)
        return widget

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
