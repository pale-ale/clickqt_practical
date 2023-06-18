import click
from clickqt.widgets.multivaluewidget import MultiValueWidget
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTabWidget
from PySide6.QtGui import QColor
from clickqt.widgets.checkbox import CheckBox
from clickqt.widgets.textfield import TextField
from clickqt.widgets.passwordfield import PasswordField
from clickqt.widgets.numericfields import IntField, RealField
from clickqt.widgets.combobox import ComboBox, CheckableComboBox
from clickqt.widgets.datetimeedit import DateTimeEdit
from clickqt.widgets.tuplewidget import TupleWidget
from clickqt.widgets.filepathfield import FilePathField
from clickqt.widgets.filefield import FileFild
from clickqt.widgets.nvaluewidget import NValueWidget
from clickqt.widgets.confirmationwidget import ConfirmationWidget
from clickqt.core.output import OutputStream, TerminalOutput
import sys

class GUI:
    def __init__(self):
        self.main_tab = QTabWidget()
        self.window = QWidget()
        self.window.setLayout(QVBoxLayout())
        self.window.layout().addWidget(self.main_tab)
 
        self.run_button = QPushButton("&Run")  # Shortcut Alt+R
        self.window.layout().addWidget(self.run_button)

        self.terminal_output = TerminalOutput()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setToolTip("Terminal output")
        self.window.layout().addWidget(self.terminal_output)
        sys.stdout = OutputStream(self.terminal_output, sys.stdout)
        sys.stderr = OutputStream(self.terminal_output, sys.stderr, QColor("red"))

    def __call__(self):
        self.window.show()
        QApplication.instance().exec()

    def create_widget(self, otype:click.ParamType, param:click.Parameter, *args, **kwargs):
        typedict = {
            click.types.BoolParamType: CheckBox,
            click.types.IntParamType: IntField,
            click.types.FloatParamType: RealField,
            click.types.StringParamType: PasswordField if hasattr(param, "hide_input") and param.hide_input else TextField,
            click.types.UUIDParameterType: TextField,
            click.types.UnprocessedParamType: TextField,
            click.types.DateTime: DateTimeEdit,
            click.types.Tuple: TupleWidget,
            click.types.Choice: ComboBox,
            click.types.Path: FilePathField,
            click.types.File: FileFild,
        }

        def get_multiarg_version(otype:click.ParamType):
            if isinstance(otype, click.types.Choice):
                return CheckableComboBox
            return NValueWidget
        
        if hasattr(param, "confirmation_prompt") and param.confirmation_prompt:
            return ConfirmationWidget(param, *args, **kwargs)
        if param.multiple:
            return get_multiarg_version(otype)(param, *args, **kwargs)
        if param.nargs > 1:
            if isinstance(otype, click.types.Tuple):
                return TupleWidget(param, *args, **kwargs)
            return MultiValueWidget(param, *args, **kwargs)

        for t,widgetclass in typedict.items():
            if isinstance(otype, t):
                return widgetclass(param, *args, **kwargs)
        raise NotImplementedError(otype)