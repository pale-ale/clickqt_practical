import click
import inspect

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox, QPushButton, QLineEdit, QGroupBox, QSpinBox, QToolTip, QComboBox


def qtgui_from_click(cmd):
    widget_registry = {}
    
    def mult_parameter_to_widget(cmd, o):
        if isinstance(o.type, click.types.BoolParamType):
            widget = QCheckBox(o.name)
            if o.default:
                widget.setChecked(True)
            widget_registry[cmd.name + '.' + o.name] = lambda: widget.isChecked()
            return widget
        
        if isinstance(o.type, click.types.StringParamType):
            if o.nargs == 2:
                widget1 = QLineEdit(o.name + '1')
                widget2 = QLineEdit(o.name + '2')
                widget = (widget1, widget2)
                widget_registry[cmd.name + '.' + o.name] = lambda: (widget1.text(), widget2.text())
            else:
                widget = QLineEdit(o.name)
                widget_registry[cmd.name + '.' + o.name] = lambda: widget.text()
            return widget
        
        if isinstance(o.type, click.types.FloatParamType):
            if o.nargs == 2:
                widget1 = QLineEdit(o.name + '1')
                widget2 = QLineEdit(o.name + '2')
                widget = (widget1, widget2)
                widget_registry[cmd.name + '.' + o.name] = lambda: (float(widget1.text()), float(widget2.text()))
            else:
                widget = QLineEdit(o.name)
                widget_registry[cmd.name + '.' + o.name] = lambda: widget.text()
            return widget
        
        if isinstance(o.type, click.types.Choice):
            widget = QComboBox()
            widget.addItems(o.type.choices)
            widget_registry[cmd.name + '.' + o.name] = lambda: widget.currentText()
            return widget

    def parameter_to_widget(o):
        if isinstance(o.type, click.types.BoolParamType):
            widget = QCheckBox(o.name)
            add_tooltip(widget, o)
            if o.default:
                widget.setChecked(True)
            widget_registry[o.name] = lambda: widget.isChecked()
            return widget

        if isinstance(o.type, click.types.IntParamType):
            widget = QSpinBox()
            add_tooltip(widget, o)
            widget_registry[o.name] = lambda: widget.value()
            return widget

        if isinstance(o.type, click.types.StringParamType):
            widget = QLineEdit(o.name)
            add_tooltip(widget, o)
            widget_registry[o.name] = lambda: widget.text()
            return widget
    
    def grouped_widgets(title, widgets):
        group = QGroupBox(title)
        group_elements = QVBoxLayout()
        group.setLayout(group_elements)
        for w in widgets:
            group_elements.addWidget(w)
        return group
    
    def mult_grouped_widgets(title, widgets):
        group = QGroupBox(title)
        group_elements = QVBoxLayout()
        group.setLayout(group_elements)
        for w in widgets:
            if isinstance(w, tuple):
                for elem in w:
                    group_elements.addWidget(elem)
            else:
                group_elements.addWidget(w)
        return group
    
    def add_tooltip(widget:QWidget, o):
        widget.setToolTip(o.help if hasattr(o, "help") else "No info available.")

    app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)
    
    if isinstance(cmd, click.Group):
        for sub_cmd in cmd.commands.values():
            required = mult_grouped_widgets(f"{sub_cmd.name}: Required arguments:", [mult_parameter_to_widget(sub_cmd, p) for p in sub_cmd.params if isinstance(p, click.core.Argument)])
            layout.addWidget(required)

            optional = mult_grouped_widgets(f"{sub_cmd.name}: Optional arguments:", [mult_parameter_to_widget(sub_cmd, p) for p in sub_cmd.params if isinstance(p, click.core.Option)])
            layout.addWidget(optional)
    else:
        required = grouped_widgets("Required arguments:", [parameter_to_widget(p) for p in cmd.params if isinstance(p, click.core.Argument)])
        layout.addWidget(required)

        optional = grouped_widgets("Optional arguments:", [parameter_to_widget(p) for p in cmd.params if isinstance(p, click.core.Option)])
        layout.addWidget(optional)

    # required = grouped_widgets("Required arguments:", [parameter_to_widget(p) for p in cmd.params if isinstance(p, click.core.Argument)])
    # layout.addWidget(required)

    # optional = grouped_widgets("Optional arguments:", [parameter_to_widget(p) for p in cmd.params if isinstance(p, click.core.Option)])
    # layout.addWidget(optional)

    app.setStyleSheet("""QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }""")

    run_button = QPushButton("&Run")
    def run():
        if isinstance(cmd, click.Group):
            for sub_cmd in cmd.commands.values():
                callback_args = []
                for arg_name in inspect.getfullargspec(sub_cmd.callback).args:
                    arg_val = widget_registry[sub_cmd.name + '.' + arg_name]()
                    callback_args.append(arg_val)
                sub_cmd.callback(*callback_args)
        else:
            for a in widget_registry: 
                print(inspect.getfullargspec(cmd.callback).args)        
            cmd.callback(*tuple(widget_registry[a]() for a in inspect.getfullargspec(cmd.callback).args))

    run_button.clicked.connect(run)

    # layout.addWidget(required)
    # layout.addWidget(optional)
    layout.addWidget(run_button)

    def run_app():
        window.show()
        app.exec()

    return run_app
