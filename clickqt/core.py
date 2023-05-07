import click
import inspect
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QLineEdit, QGroupBox, QLabel, QComboBox

from clickqt.checkableComboBox import CheckableComboBox


def qtgui_from_click(cmd):
    widget_registry = {}

    def parameter_to_widget(o):
        if o.name: # CLI-Parameter has a name
            param = QWidget()
            hBox = QHBoxLayout()
            widget = None
            param.setLayout(hBox)
            label = QLabel(f"{o.name}: ")
            if hasattr(o, "help"): # Only options have a help argument
                label.setToolTip(o.help)
            hBox.addWidget(label)
         
            match o.type:
                case click.types.BoolParamType():
                    widget = QCheckBox()
                    if o.default() if callable(o.default) else o.default:
                        widget.setChecked(True)
                    widget_registry[o.name] = lambda: widget.isChecked()
                case click.types.StringParamType():
                    widget = QLineEdit(o.default() if callable(o.default) else o.default)
                    if hasattr(o, "hide_input"): # Only options have a hide_input argument
                        widget.setEchoMode(QLineEdit.EchoMode.Password)
                    widget_registry[o.name] = lambda: widget.text()
                case click.types.IntRange():
                    widget = QLineEdit()
                    widget_registry[o.name] = lambda: len(widget.text()) if not widget.text().isnumeric() else int(widget.text())
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
    
    def grouped_widgets(title, widgets):
        if len(widgets):
            group = QGroupBox(title)
            group_elements = QVBoxLayout()
            group.setLayout(group_elements)
            for w in widgets:
                group_elements.addWidget(w)
            return group
        return None
    
    app = QApplication([])
    app.setApplicationName("GUI for CLI")
    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)

    required = grouped_widgets("Required arguments:", [parameter_to_widget(p) for p in cmd.params if isinstance(p, click.core.Argument) or (isinstance(p, click.core.Option) and p.required)])
    if required:
        layout.addWidget(required)

    optional = grouped_widgets("Optional arguments:", [parameter_to_widget(p) for p in cmd.params if isinstance(p, click.core.Option) and not p.required])
    if optional:
        layout.addWidget(optional)

    run_button = QPushButton("&Run")    #Shortcut Alt+R
    def run():
        cmd.callback(*tuple(widget_registry[a]() for a in inspect.getfullargspec(cmd.callback).args))
        app.quit()  #Close GUI

    run_button.clicked.connect(run)

    layout.addWidget(run_button)

    def run_app():
        window.show()
        app.exec()

    return run_app
