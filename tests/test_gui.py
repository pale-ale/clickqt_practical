import click
import pytest
import clickqt

from tests.testutils import ClickAttrs
from PySide6.QtWidgets import QTabWidget, QPushButton, QSplitter, QWidget, QApplication
from PySide6.QtCore import Qt
from clickqt.core.output import TerminalOutput
from clickqt.core.control import Control
from typing import Iterable
import clickqt.widgets
import time


def findChildren(object: QWidget, child_type: QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly) -> Iterable:
    return object.findChildren(child_type, options=options)

def checkLen(children: Iterable, expected_len:int) -> Iterable:
    assert len(children) == expected_len
    return children

def hasWidgets(tab_widget_content:QWidget, control:Control, group_hierarchy_name:str, params:list[click.Parameter]) -> tuple[bool, str]:
    for param in params:
        # Search for the widget of type 'widget_type' and name 'widget_name' recursively
        children = tab_widget_content.findChildren(control.widget_registry[group_hierarchy_name][param.name].widget_type, (control.widget_registry[group_hierarchy_name][param.name].widget_name))

        if len(children) == 0:
            return (False, f"Widget is missing in QTabWidget: '{param.name}'")
        elif isinstance(control.widget_registry[group_hierarchy_name][param.name], clickqt.widgets.ConfirmationWidget):
            if len(children) != 1+2: # Container widget and the two normal widgets
                return (False, f"ConfirmationWidget is multiple times in QTabWidget: '{param.name}'")       
        elif len(children) != 1:
            return (False, f"Widget is multiple times in QTabWidget: '{param.name}'")

    return (True, "")

def isIncluded(tab_widget:QTabWidget|QWidget, expected_group_command:list[click.Group|click.Command], control:Control, group_hierarchy_name:str) -> tuple[bool, str]:
    if type(tab_widget) is QWidget: # Group has options
        tab_widget = checkLen(findChildren(tab_widget, QTabWidget), 1)[0]

    assert tab_widget.count() == len(expected_group_command) # amount of tabs == amount of commands and groups

    for group_command in expected_group_command:
        # group_command.name is the name of one tab
        for i in range(tab_widget.count()):
            tab_widget_name = tab_widget.tabText(i)

            if tab_widget_name == group_command.name:
                res = hasWidgets(tab_widget.widget(i), control, control.concat(group_hierarchy_name, group_command.name), group_command.params)
                if not res[0]:
                    return res  

                break # Skips the else block
        else:
            return (False, f"Command-/Group name is missing in QTabWidget: '{group_command.name}'")

        # Recursive call for groups
        if isinstance(group_command, click.Group):
            res = isIncluded(next(filter(lambda x: isinstance(x, QTabWidget) or type(x) is QWidget, [tab_widget.widget(i) for i in range(tab_widget.count())])), 
                              group_command.commands.values(), control, control.concat(group_hierarchy_name, group_command.name))
            if not res[0]:
                return res    
                
    return (True, "")


@pytest.mark.parametrize(
    ("root_group_command"),
    [
        (click.Command("cli", params=[])),
        (click.Group("group", commands=[
            click.Command("cli", params=[])
            ])),
        (click.Group("root_group", commands=[
            click.Group("sub_group", commands=[
                click.Command("sub_cli", params=[])
                ]), 
            click.Command("cli", params=[])
            ])),
        (click.Group("root_group", commands=[
            click.Command("cli1", params=[]),
            click.Command("cli2", params=[]),
            click.Group("sub_group", commands=[
                click.Command("sub_cli1", params=[]),
                click.Command("sub_cli2", params=[]),
                click.Group("sub_sub_group", commands=[
                    click.Command("sub_sub_cli1", params=[]),
                    click.Command("sub_sub_cli2", params=[]),
                    ]), 
                ]), 
            ])),
    ]
)
def test_gui_construction_no_options(root_group_command: click.Group|click.Command):
    control = clickqt.qtgui_from_click(root_group_command)
    gui = control.gui

    # Base widgets are set correctly
    assert checkLen(findChildren(gui.window, QSplitter), 1)[0] == gui.splitter
    buttons = checkLen(findChildren(gui.splitter, QPushButton, Qt.FindChildOption.FindChildrenRecursively), 2)
    assert gui.run_button in buttons and gui.stop_button in buttons
    assert checkLen(findChildren(gui.splitter, TerminalOutput), 1)[0] == gui.terminal_output

    parent_tab_widget = checkLen(findChildren(gui.splitter, QTabWidget), 1)[0]
    assert parent_tab_widget == gui.main_tab and parent_tab_widget.tabText(0) == root_group_command.name

    # Check for right amount of QTabWidgets-instances with correct tab-names
    if isinstance(root_group_command, click.Group) and len(root_group_command.commands.values()) > 1:
        tab_widget = next(filter(lambda x: isinstance(x, QTabWidget) or type(x) is QWidget, [parent_tab_widget.widget(i) for i in range(parent_tab_widget.count())]))
        
        included, err_message = isIncluded(tab_widget, root_group_command.commands.values(), control, root_group_command.name) 

        assert included, err_message

@pytest.mark.parametrize(
    ("root_group_command"),
    [
        (click.Command("cli", params=[click.Option(param_decls=["--test1"], **ClickAttrs.checkbox()), click.Option(param_decls=["--test2"], **ClickAttrs.intfield())])),
        (click.Group("group",  params=[click.Option(param_decls=["--abc1"], **ClickAttrs.realfield()), 
                                       click.Option(param_decls=["--abc2"], **ClickAttrs.textfield())], commands=[
            click.Command("cli", params=[click.Option(param_decls=["--abc1"], **ClickAttrs.passwordfield()), 
                                         click.Option(param_decls=["--abc2"], **ClickAttrs.combobox(choices=["A", "B"]))]) # Same option names are allowed
            ])),
        (click.Group("root_group", params=[click.Option(param_decls=["--root1"], **ClickAttrs.datetime()), 
                                       click.Option(param_decls=["--root2"], **ClickAttrs.uuid())], commands=[
            click.Group("sub_group", params=[click.Option(param_decls=["--group1"], **ClickAttrs.intrange()), 
                                       click.Option(param_decls=["--group2"], **ClickAttrs.floatrange())], commands=[
                click.Command("sub_cli", params=[click.Option(param_decls=["--abc1"], **ClickAttrs.tuple_widget(types=(click.types.Path(),int))), 
                                       click.Option(param_decls=["--abc2"], **ClickAttrs.multi_value_widget(nargs=2))])
                ]), 
            click.Command("cli", params=[click.Option(param_decls=["--abc2"], **ClickAttrs.confirmation_widget())])
            ])),
        (click.Group("root_group", params=[click.Option(param_decls=["--group1"], **ClickAttrs.datetime())], commands=[
            click.Command("cli1", params=[click.Option(param_decls=["--group1"], **ClickAttrs.multi_value_widget(nargs=2))]),
            click.Command("cli2", params=[]),
            click.Group("sub_group", params=[click.Option(param_decls=["--group1"], **ClickAttrs.filefield()), 
                                       click.Option(param_decls=["--group2"], **ClickAttrs.filepathfield())], commands=[
                click.Command("sub_cli1", params=[click.Option(param_decls=["--cli"], **ClickAttrs.nvalue_widget())]),
                click.Command("sub_cli2", params=[]),
                click.Group("sub_sub_group", params=[click.Option(param_decls=["--group1"], **ClickAttrs.checkbox()),
                                       click.Option(param_decls=["--group2"], **ClickAttrs.intrange())], commands=[
                    click.Command("sub_sub_cli1", params=[]),
                    click.Command("sub_sub_cli2", params=[click.Option(param_decls=["--cli2"], **ClickAttrs.tuple_widget(types=(click.types.FloatRange(),int)))]),
                    ]), 
                ]), 
            ])),
    ]
)
def test_gui_construction_with_options(root_group_command: click.Group|click.Command):
    control = clickqt.qtgui_from_click(root_group_command)
    gui = control.gui

    parent_tab_widget = checkLen(findChildren(gui.splitter, QTabWidget), 1)[0]
    hasWidgets(parent_tab_widget.widget(0), control, root_group_command.name, root_group_command.params)

    # Check for right amount of QTabWidgets-instances with correct tab-names and correct widget objects
    if isinstance(root_group_command, click.Group) and len(root_group_command.commands.values()) > 1:
        tab_widget = next(filter(lambda x: isinstance(x, QTabWidget) or type(x) is QWidget, [parent_tab_widget.widget(i) for i in range(parent_tab_widget.count())]))
        
        included, err_message = isIncluded(tab_widget, root_group_command.commands.values(), control, root_group_command.name) 

        assert included, err_message

def test_gui_stop_execution():
    param = click.Option(param_decls=["--p"], **ClickAttrs.checkbox())
    cli = click.Command("cli", params=[param], callback=lambda p: time.sleep(5))

    control = clickqt.qtgui_from_click(cli)
    run_button = control.gui.run_button
    stop_button = control.gui.stop_button

    assert run_button.isEnabled() and not stop_button.isEnabled()
    assert control.worker is None and control.worker_thread is None

    run_button.click() # Start execution

    assert not run_button.isEnabled() and stop_button.isEnabled()
    assert control.worker is not None and control.worker_thread is not None

    stop_button.click() # Stop execution

    for _ in range(10):  # Wait for stopping the worker
        QApplication.processEvents()
        time.sleep(0.0001)

    assert run_button.isEnabled() and not stop_button.isEnabled()
    assert control.worker is None and control.worker_thread is None
    assert "Execution stopped!\n" in control.gui.terminal_output.toPlainText()

    """run_button.click() # Start execution

    for _ in range(10):  # Wait for starting the worker
        QApplication.processEvents()
        time.sleep(0.0001)

    assert not run_button.isEnabled() and stop_button.isEnabled()
    assert control.worker is not None and control.worker_thread is not None
    
    spy = QSignalSpy(control.worker, SIGNAL("finished()"))

    # Wait for the worker to finish
    for _ in range(10):
        if not spy.count():
            QApplication.processEvents()
            spy.wait(200)

    assert run_button.isEnabled() and not stop_button.isEnabled()
    assert control.worker is None and control.worker_thread is None"""
