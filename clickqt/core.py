import click
import inspect

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox, QPushButton, QLineEdit, QGroupBox


def qtgui_from_click(cmd):
    widget_registry = {}

    def parameter_to_widget(o):
        if isinstance(o.type, click.types.BoolParamType):
            widget = QCheckBox(o.name)
            if o.default:
                widget.setChecked(True)
            widget_registry[o.name] = lambda: widget.isChecked()
            return widget
        
        if isinstance(o.type, click.types.StringParamType):
            widget = QLineEdit(o.name)
            widget_registry[o.name] = lambda: widget.text()
            return widget
    
    def grouped_widgets(title, widgets):
        group = QGroupBox(title)
        group_elements = QVBoxLayout()
        group.setLayout(group_elements)
        for w in widgets:
            group_elements.addWidget(w)
        return group
    
    app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)

    required = grouped_widgets("Required arguments:", [parameter_to_widget(p) for p in cmd.params if isinstance(p, click.core.Argument)])
    layout.addWidget(required)

    optional = grouped_widgets("Optional arguments:", [parameter_to_widget(p) for p in cmd.params if isinstance(p, click.core.Option)])
    layout.addWidget(optional)

    run_button = QPushButton("&Run")
    def run():
        cmd.callback(*tuple(widget_registry[a]() for a in inspect.getfullargspec(cmd.callback).args))

    run_button.clicked.connect(run)

    layout.addWidget(required)
    layout.addWidget(optional)
    layout.addWidget(run_button)

    def run_app():
        window.show()
        app.exec()

    return run_app
