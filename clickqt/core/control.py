from __future__ import annotations

import typing as t
import sys
from functools import reduce
import re
import inspect
import click
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QVBoxLayout,
    QTabWidget,
    QScrollArea,
    QApplication,
    QSizePolicy,
    QLabel,
)
from PySide6.QtCore import QThread, QObject, Signal, Slot, Qt
from PySide6.QtGui import QPalette, QClipboard

from clickqt.core.gui import GUI
from clickqt.core.commandexecutor import CommandExecutor
from clickqt.core.error import ClickQtError
from clickqt.widgets.combobox import CheckableComboBox, ComboBox
from clickqt.widgets.basewidget import BaseWidget
from clickqt.widgets.messagebox import MessageBox
from clickqt.widgets.filefield import FileField
from clickqt.core.utils import is_nested_list, is_file_path


class Control(QObject):
    """Regulates the creation of the GUI with their widgets according to clicks parameter types and causes the execution/abortion of a selected command.

    :param cmd: The callback function from which a GUI should be created
    """

    #: Internal Qt-signal, which will be emitted when the :func:`~clickqt.core.control.Control.start_execution`-Slot was triggered and executed successfully.
    requestExecution: Signal = Signal(list, click.Context)  # Generics do not work here

    def __init__(
        self, cmd: click.Command, is_ep: bool = True, ep_or_path: str = "test"
    ):
        """Initializing the GUI object and the registries together with the differentiation of a group command and a simple command."""

        super().__init__()

        self.gui = GUI()
        self.cmd = cmd

        self.is_ep = is_ep
        self.ep_or_path = ep_or_path

        # Create a worker in another thread when the user clicks the run button
        # Don't destroy a thread when no command is running and the user closes the application
        # Otherwise "QThread: Destroyed while thread is still running" would be appear
        self.worker_thread: QThread = None
        self.worker: CommandExecutor = None

        # Connect GUI buttons with slots
        self.gui.run_button.clicked.connect(self.start_execution)
        self.gui.stop_button.clicked.connect(self.stop_execution)
        self.gui.copy_button.clicked.connect(self.construct_command_string)

        # Groups-Command-name concatinated with ":" to command-option-names to BaseWidget
        self.widget_registry: dict[str, dict[str, BaseWidget]] = {}
        self.command_registry: dict[str, dict[str, tuple[int, t.Callable]]] = {}

        # Add all widgets
        self.parse(self.gui.widgets_container, cmd, cmd.name)

        self.gui.construct()

    def __call__(self):
        """Shows the GUI according to :func:`~clickqt.core.gui.GUI.__call__` of :class:`~clickqt.core.gui.GUI`."""

        self.gui()

    def set_ep_or_path(self, ep_or_path):
        self.ep_or_path = ep_or_path

    def set_is_ep(self, is_ep):
        self.is_ep = is_ep

    def parameter_to_widget(
        self, command: click.Command, groups_command_name: str, param: click.Parameter
    ) -> QWidget:
        """Creates a clickqt widget according to :func:`~clickqt.core.gui.GUI.create_widget` and returns the container of the widget (label-element + Qt-widget).

        :param command: The click command of the provided **param**
        :param groups_command_name: The hierarchy of the **command** as string whereby the names of the components are
                                    concatenated according to :func:`~clickqt.core.control.Control.concat`
        :param param: The click parameter whose type a clickqt widget should be created from

        :return: The container of the created widget (label-element + Qt-widget)
        """

        assert param.name, "No parameter name specified"
        assert self.widget_registry[groups_command_name].get(param.name) is None

        widget = self.gui.create_widget(
            param.type, param, widgetsource=self.gui.create_widget, com=command
        )
        self.widget_registry[groups_command_name][param.name] = widget
        self.command_registry[groups_command_name][param.name] = (
            param.nargs,
            type(param.type).__name__,
        )

        return widget.container

    def concat(self, a: str, b: str) -> str:  # pylint: disable=no-self-use
        """Concatenates the strings a and b with ':' and returns the result."""

        return a + ":" + b

    def parse(
        self,
        tab_widget: QWidget,
        cmd: click.Command,
        group_name: str,
        group_names_concatenated: str = "",
    ):
        if isinstance(cmd, click.Group):
            child_tabs: QWidget = None
            concat_group_names = (
                self.concat(group_names_concatenated, group_name)
                if group_names_concatenated
                else group_name
            )
            if len(cmd.params) > 0:
                child_tabs = QWidget()
                child_tabs.setLayout(QVBoxLayout())
                group_params = self.parse_cmd(cmd, concat_group_names)
                group_params.widget().layout().setContentsMargins(0, 0, 0, 0)
                group_params.setSizePolicy(
                    QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
                )  # Group params don't have to be resizable
                child_tabs.layout().addWidget(group_params)
                child_tabs.layout().addWidget(
                    self.parse_cmd_group(cmd, concat_group_names)
                )
            else:
                child_tabs = self.parse_cmd_group(cmd, concat_group_names)

            child_tabs.setAutoFillBackground(True)
            child_tabs.setBackgroundRole(
                QPalette.ColorRole.Window
            )  # Remove white spacing between widgets

            if tab_widget == self.gui.widgets_container:
                self.gui.widgets_container = child_tabs
            else:
                tab_widget.addTab(child_tabs, group_name)
        elif tab_widget == self.gui.widgets_container:
            self.gui.widgets_container = self.parse_cmd(cmd, cmd.name)
        else:
            tab_widget.addTab(
                self.parse_cmd(
                    cmd,
                    self.concat(group_names_concatenated, cmd.name)
                    if group_names_concatenated
                    else cmd.name,
                ),
                group_name,
            )

    def parse_cmd_group(
        self, cmdgroup: click.Group, group_names_concatenated: str
    ) -> QTabWidget:
        """Creates for every group in **cmdgroup** a QTabWidget instance and adds every command in **cmdgroup** as a tab to it.
        The creation of the content of every tab is realized by calling :func:`~clickqt.core.control.Control.parse_cmd`.
        To realize command hierachies, this method is called recursively.

        :param cmdgroup: The group from which a QTabWidget with content should be created
        :param group_names_concatenated: The hierarchy of **cmdgroup** as string whereby the names of the components are
                                         concatenated according to :func:`~clickqt.core.control.Control.concat`

        :returns: A Qt-GUI representation in a QTabWidget of **cmdgroup**
        """

        group_tab_widget = QTabWidget()
        for group_name, group_cmd in cmdgroup.commands.items():
            self.parse(
                group_tab_widget, group_cmd, group_name, group_names_concatenated
            )

        return group_tab_widget

    def parse_cmd(self, cmd: click.Command, groups_command_name: str) -> QScrollArea:
        """Creates for every click parameter in **cmd** a clickqt widget and returns them stored in a QScrollArea.
        The widgets are divided into a "Required arguments" and "Optional arguments" part.

        :param cmd: The command from which a QTabWidget with content should be created
        :param groups_command_name: The hierarchy of **cmd** as string whereby the names of the components are
                                    concatenated according to :func:`~clickqt.core.control.Control.concat`

        :returns: The created clickqt widgets stored in a QScrollArea
        """

        cmdbox = QWidget()
        cmdbox.setLayout(QVBoxLayout())
        cmdbox.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        required_optional_box: list[QWidget] = []

        for i in range(2):
            box = QWidget()
            box.setLayout(QVBoxLayout())
            box_label = QLabel(
                text=f"<b>{'Required arguments' if i == 0 else 'Optional arguments'}</b>"
            )
            box_label.setTextFormat(Qt.TextFormat.RichText)  # Bold text
            box.layout().addWidget(box_label)
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            box.layout().addWidget(line)
            box.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

            required_optional_box.append(box)

        INITIAL_CHILD_WIDGETS = len(
            required_optional_box[0].children()
        )  # layout, label, line

        assert (
            self.widget_registry.get(groups_command_name) is None
        ), f"Not a unique group_command_name_concat ({groups_command_name})"

        self.widget_registry[groups_command_name] = {}
        self.command_registry[groups_command_name] = {}

        # parameter name to flag values
        feature_switches: dict[str, list[click.Parameter]] = {}

        for param in cmd.params:
            if isinstance(param, click.core.Parameter):
                if (
                    hasattr(param, "is_flag")
                    and param.is_flag
                    and hasattr(param, "flag_value")
                    and isinstance(param.flag_value, str)
                    and param.flag_value
                ):  # clicks feature switches
                    if feature_switches.get(param.name) is None:
                        feature_switches[param.name] = []
                    feature_switches[param.name].append(param)
                else:
                    required_optional_box[
                        0
                        if (param.required or isinstance(param, click.Argument))
                        and param.default is None
                        else 1
                    ].layout().addWidget(
                        self.parameter_to_widget(cmd, groups_command_name, param)
                    )

        # Create for every feature switch a ComboBox
        for param_name, switch_names in feature_switches.items():
            choice = click.Option(
                [f"--{param_name}"],
                type=click.Choice([x.flag_value for x in switch_names]),
                required=reduce(lambda x, y: x | y.required, switch_names, False),
            )
            default = next(
                (x.flag_value for x in switch_names if x.default),
                switch_names[0].flag_value,
            )  # First param with default==True is the default
            required_optional_box[0 if choice.required else 1].layout().addWidget(
                self.parameter_to_widget(cmd, groups_command_name, choice)
            )
            self.widget_registry[groups_command_name][param_name].set_value(default)

        for box in required_optional_box:
            if len(box.children()) > INITIAL_CHILD_WIDGETS:
                cmdbox.layout().addWidget(box)

        cmd_tab_widget = QScrollArea()
        cmd_tab_widget.setFrameShape(QFrame.Shape.NoFrame)  # Remove black border
        cmd_tab_widget.setBackgroundRole(QPalette.ColorRole.Window)
        cmd_tab_widget.setWidgetResizable(True)  # Widgets should use the whole area
        cmd_tab_widget.setWidget(cmdbox)

        return cmd_tab_widget

    def check_error(self, err: ClickQtError) -> bool:
        """Checks whether **err** contains an error and prints on error case the message of it to sys.stderr.

        :return: True, if **err** contains an error, False otherwise"""

        if err.type != ClickQtError.ErrorType.NO_ERROR:
            if message := err.message():  # Don't print on context exit
                print(message, file=sys.stderr)
            return True

        return False

    def current_command_hierarchy(
        self, tab_widget: QWidget, cmd: click.Command
    ) -> list[click.Command]:
        """Returns the hierarchy of the command of the selected tab as list whereby the order of the list is from root command
        to the selected command.

        :param tab_widget: The currend widget of the root-QTabWidget
        :param cmd: The click command provided to :func:`~clickqt.core.control.Control`

        :return: The hierarchy of the command of the selected tab as ordered list (root command to selected command)
        """

        if isinstance(cmd, click.Group):
            if len(cmd.params) > 0:  # Group has params
                tab_widget = tab_widget.findChild(QTabWidget)

            assert isinstance(tab_widget, QTabWidget)

            command = cmd.get_command(
                ctx=None, cmd_name=tab_widget.tabText(tab_widget.currentIndex())
            )

            return [cmd] + self.current_command_hierarchy(
                tab_widget.currentWidget(), command
            )

        return [cmd]

    def get_option_names(self, cmd):
        """Returns an array of all the parameters used for the current command togeter with their properties."""
        option_names = []
        for param in cmd.params:
            if isinstance(param, click.Option):
                long_forms = [opt for opt in param.opts if opt.startswith("--")]
                longest_long_form = max(long_forms, key=len) if long_forms else None
                short_forms = [opt for opt in param.opts if opt.startswith("-")]
                short_forms = max(short_forms, key=len) if short_forms else None
                if longest_long_form:
                    option_names.append(
                        (
                            longest_long_form,
                            param.type,
                            param.multiple,
                            param.nargs,
                            param.confirmation_prompt,
                        )
                    )
                else:
                    option_names.append(
                        (
                            short_forms,
                            param.type,
                            param.multiple,
                            param.nargs,
                            param.confirmation_prompt,
                        )
                    )
            elif isinstance(param, click.Argument):
                option_names.append(("Argument", param.type))
        return option_names

    def get_params(self, selected_command_name: str, args):
        """Returns an array of strings that are used for the output field."""
        params = [k for k, v in self.widget_registry[selected_command_name].items()]
        if "yes" in params:
            params.remove("yes")
        command_help = self.command_registry.get(selected_command_name)
        tuples_array = list(command_help.values())
        for i, param in enumerate(args):
            params[i] = "--" + param + f": {tuples_array[i]}: " + f"{args[param]}"
        return params

    def clean_command_string(self, word, text):
        """Returns a string without any special characters using regex."""
        text = re.sub(r"\b{}\b".format(re.escape(word)), "", text)
        text = re.sub(r"[^a-zA-Z0-9 .-]", " ", text)
        return text

    def command_to_string(self, hierarchy_selected_command_name: str):
        """Returns the current command name."""
        hierarchy_selected_command_name = self.clean_command_string(
            self.cmd.name, hierarchy_selected_command_name
        )
        return self.ep_or_path + " " + hierarchy_selected_command_name

    def command_to_string_to_copy(self, hierarchy_selected_name: str, selected_command):
        """Returns a string representing the click command if one actually would actually execute it in the shell."""
        parameter_list = self.get_option_names(selected_command)
        parameter_list = [param for param in parameter_list if param[0] != "--yes"]
        widgets = self.widget_registry[hierarchy_selected_name]
        widget_keys = list(widgets.keys())
        if "yes" in widgets:
            widgets.pop("yes")
        widget_values = []
        for widget in widgets:
            if widget != "yes":
                widget_values.append(widgets[widget].get_widget_value())
        parameter_strings = []
        for i, param in enumerate(parameter_list):
            if param[0] == "Argument":
                parameter_strings.append(str(widget_values[i]))
                continue
            if (not isinstance(widget_values[i], list)) and param[2] is not True:
                widget_value = str(widget_values[i])
                if (isinstance(param[1], click.Choice) and param[4] is True) or (
                    isinstance(param[1], click.Choice)
                ):
                    if is_file_path(widget_value):
                        parameter_strings.append(param[0] + "=" + widget_value)
                    else:
                        parameter_strings.append(
                            param[0]
                            + "="
                            + re.sub(r"[^a-zA-Z0-9 .-]", " ", widget_value)
                        )
                else:
                    if is_file_path(widget_value):
                        parameter_strings.append(param[0] + " " + widget_value)
                    else:
                        parameter_strings.append(
                            param[0]
                            + " "
                            + re.sub(r"[^a-zA-Z0-9 .-]", " ", widget_value)
                        )
            else:
                if is_nested_list(widget_values[i]):
                    depth = len(widget_values[i])
                    for j in range(depth):
                        widget_value = str(widget_values[i][j])
                        if not is_file_path(widget_value):
                            parameter_strings.append(
                                param[0]
                                + " "
                                + re.sub(r"[^a-zA-Z0-9 .-]", " ", widget_value)
                            )
                        else:
                            parameter_strings.append(param[0] + " " + widget_value)
                else:
                    length = len(widget_values[i])
                    if param[2] is not True:
                        parameter_strings.append(param[0])
                        for j in range(length):
                            widget_value = str(widget_values[i][j])
                            if not is_file_path(widget_value):
                                parameter_strings.append(
                                    " " + re.sub(r"[^a-zA-Z0-9 .-]", " ", widget_value)
                                )
                            else:
                                parameter_strings.append(" " + widget_value)
                    else:
                        if isinstance(widgets[widget_keys[i]], CheckableComboBox):
                            for j in range(length):
                                widget_value = str(widget_values[i][j])
                                if not is_file_path(widget_value):
                                    parameter_strings.append(
                                        param[0]
                                        + "="
                                        + re.sub(r"[^a-zA-Z0-9 .-]", " ", widget_value)
                                    )
                                else:
                                    parameter_strings.append(
                                        param[0] + "=" + widget_value
                                    )
                        else:
                            for j in range(length):
                                widget_value = str(widget_values[i][j])
                                if not is_file_path(widget_value):
                                    parameter_strings.append(
                                        param[0]
                                        + " "
                                        + re.sub(r"[^a-zA-Z0-9 .-]", " ", widget_value)
                                    )
                                else:
                                    parameter_strings.append(
                                        param[0] + " " + widget_value
                                    )
        message = hierarchy_selected_name + " " + " ".join(parameter_strings)
        message = re.sub(r"\b{}\b".format(re.escape(self.cmd.name)), "", message)
        message = message.replace(":", " ")
        if not self.is_ep:
            message = "python " + self.ep_or_path + " " + message
        else:
            message = self.ep_or_path + " " + message
        return message

    def function_call_formatter(
        self, hierarchy_selected_command_name: str, selected_command_name: str, args
    ):
        params = self.get_params(hierarchy_selected_command_name, args)
        message = f"{selected_command_name} \n"
        parameter_message = "Current Command parameters: \n" + "\n".join(params)
        return message + parameter_message

    @Slot()
    def stop_execution(self):
        """Qt-Slot, which stops the execution of the command(-hierarchy) which is currently running."""

        print("Execution stopped!", file=sys.stderr)
        self.worker_thread.terminate()
        self.execution_finished()

    @Slot()
    def execution_finished(self):
        """Qt-Slot, which deletes the internal worker-object and resets the buttons of the GUI.
        This slot is automatically executed when the execution of a command has finished.
        """

        self.worker_thread.deleteLater()
        self.worker.deleteLater()

        self.worker_thread = None
        self.worker = None

        self.gui.run_button.setEnabled(True)
        self.gui.stop_button.setEnabled(False)

    @Slot()
    def start_execution(self):
        """Qt-Slot, which validates the selected command hierarchy and causes (on success) their execution in another thread by
        emitting the :func:`~clickqt.core.control.Control.requestExecution`-Signal. Widgets that will show a dialog will be validated at last.
        This slot is automatically executed when the user clicks on the 'Run'-button.
        """

        hierarchy_selected_command = self.current_command_hierarchy(
            self.gui.widgets_container, self.cmd
        )

        def run_command(
            command: click.Command, hierarchy_command: str
        ) -> t.Optional[t.Callable]:
            kwargs: dict[str, t.Any] = {}
            has_error = False
            dialog_widgets: list[BaseWidget] = []  # widgets that will show a dialog

            if (
                self.widget_registry.get(hierarchy_command) is not None
            ):  # Groups with no options are not in the dict
                # Check the values of all non dialog widgets for errors
                for option_name, widget in self.widget_registry[
                    hierarchy_command
                ].items():
                    if isinstance(widget, MessageBox):
                        dialog_widgets.append(
                            widget
                        )  # MessageBox widgets should be shown at last
                    elif (
                        isinstance(widget, FileField)
                        and "r" in widget.type.mode
                        and widget.get_widget_value() == "-"
                    ):
                        dialog_widgets.insert(
                            0, widget
                        )  # FileField widgets with input dialog should be shown at last, but before MessageBox widgets
                    else:
                        widget_value, err = widget.get_value()
                        has_error |= self.check_error(err)

                        if widget.param.expose_value:
                            kwargs[option_name] = widget_value

                if has_error:
                    return None

                # Now check the values of all dialog widgets for errors
                for widget in dialog_widgets:
                    widget_value, err = widget.get_value()
                    if isinstance(widget, FileField):
                        assert callable(widget_value)
                        widget_value, err = widget_value()

                    if self.check_error(err):
                        return None

                    if widget.param.expose_value:
                        kwargs[widget.param.name] = widget_value

            if len(callback_args := inspect.getfullargspec(command.callback).args) > 0:
                args: list[t.Any] = []
                for ca in callback_args:  # Bring the args in the correct order
                    args.append(
                        kwargs.pop(ca)
                    )  # Remove explicitly mentioned args from kwargs

                    print(
                        f"For command details, please call '{self.command_to_string(hierarchy_command)} --help'"
                    )
                    print(self.command_to_string_to_copy(hierarchy_command, command))
                    print(
                        f"Current Command: {self.function_call_formatter(hierarchy_command, command, kwargs)} \n"
                        + "Output:"
                    )
                    return lambda: command.callback(*args, **kwargs)
            else:
                return lambda: command.callback(
                    **kwargs
                )  # pylint: disable=unnecessary-lambda

        callables: list[t.Callable] = []
        for i, command in enumerate(hierarchy_selected_command, 1):
            if (
                c := run_command(
                    command,
                    reduce(
                        self.concat, [g.name for g in hierarchy_selected_command[:i]]
                    ),
                )
            ) is not None:
                callables.append(c)

        if len(callables) == len(hierarchy_selected_command):
            self.gui.run_button.setEnabled(False)
            self.gui.stop_button.setEnabled(True)

            self.worker_thread = QThread()
            self.worker_thread.start()
            self.worker = CommandExecutor()
            self.worker.moveToThread(self.worker_thread)
            self.worker.finished.connect(self.worker_thread.quit)
            self.worker.finished.connect(self.execution_finished)
            self.requestExecution.connect(self.worker.run)

            self.requestExecution.emit(
                callables, click.Context(hierarchy_selected_command[-1])
            )

    def construct_command_string(self):
        """
        This function is responsible
        """
        hierarchy_selected_command = self.current_command_hierarchy(
            self.gui.widgets_container, self.cmd
        )
        selected_command = hierarchy_selected_command[-1]
        hierarchy_selected_command_name = reduce(
            self.concat, [g.name for g in hierarchy_selected_command]
        )

        kwargs: dict[str, t.Any] = {}
        has_error = False
        unused_options: list[BaseWidget] = []  # parameters with expose_value==False

        # Check all values for errors
        for option_name, widget in self.widget_registry[
            hierarchy_selected_command_name
        ].items():
            param: click.Parameter = next(
                (x for x in selected_command.params if x.name == option_name)
            )
            if param.expose_value:
                widget_value, err = widget.get_value()
                has_error |= self.check_error(err)

                kwargs[option_name] = widget_value
            else:  # Verify it when all options are valid
                unused_options.append(widget)

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
        for widget in unused_options:
            widget_value, err = widget.get_value()
            has_error |= self.check_error(err)
            if callable(widget_value):
                _, err = widget_value()
                has_error |= self.check_error(err)

        if has_error:
            return

        message = self.command_to_string_to_copy(
            hierarchy_selected_command_name, selected_command
        )
        clip_board = QApplication.clipboard()
        clip_board.setText(message, QClipboard.Clipboard)
