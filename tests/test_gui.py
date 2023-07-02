import click
import pytest
import clickqt

from PySide6.QtWidgets import QTabWidget, QPushButton, QSplitter, QWidget
from PySide6.QtCore import Qt
from clickqt.core.output import TerminalOutput
from typing import Iterable, Any


@pytest.mark.parametrize(
    ("root_group_command", "expected_groups_commands"),
    [
        (click.Command("cli", params=[]), ["cli"]),
        (click.Group("group", commands=[
            click.Command("cli", params=[])
            ]), ["group", ["cli"]]),
        (click.Group("root_group", commands=[
            click.Group("sub_group", commands=[
                click.Command("sub_cli", params=[])
                ]), 
            click.Command("cli", params=[])
            ]), ["root_group", ["sub_group", ["sub_cli"], "cli"]]),
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
            ]), ["root_group", ["cli1", "cli2", "sub_group", ["sub_cli1", "sub_cli2", "sub_sub_group", ["sub_sub_cli1", "sub_sub_cli2"]]]]),
    ]
)
def test_gui_construction(root_group_command: click.Group|click.Command, expected_groups_commands:list[Any]):
    control = clickqt.qtgui_from_click(root_group_command)
    gui = control.gui

    def findChildren(object: QWidget, child_type: QWidget) -> Iterable:
        return object.findChildren(child_type, options=Qt.FindChildOption.FindDirectChildrenOnly)
    
    def checkLen(children: Iterable, expected_len:int) -> Iterable:
        assert len(children) == expected_len
        return children
    
    def isIncluded(tab_widget:QTabWidget, expected_group_command_names:list[str]):
        assert tab_widget.count() == sum(1 for y in expected_group_command_names if isinstance(y, str))

        for name in expected_group_command_names:
            if not isinstance(name, str):
                if not isIncluded(next(filter(lambda x: isinstance(x, QTabWidget), [tab_widget.widget(i) for i in range(tab_widget.count())])), name):
                    return False
                else:
                    continue
            else:
                for i in range(tab_widget.count()):
                    tab_widget_name = tab_widget.tabText(i)

                    if tab_widget_name == name:
                        break # Skips the else block
                else:
                    return False
                    
        return True

    assert checkLen(findChildren(gui.window, QSplitter), 1)[0] == gui.splitter
    assert checkLen(findChildren(gui.splitter, QPushButton), 1)[0] == gui.run_button
    assert checkLen(findChildren(gui.splitter, TerminalOutput), 1)[0] == gui.terminal_output

    parent_tab_widget = checkLen(findChildren(gui.splitter, QTabWidget), 1)[0]
    assert parent_tab_widget == gui.main_tab and parent_tab_widget.tabText(0) == expected_groups_commands[0]

    if len(expected_groups_commands) > 1:
        tab_widget = next(filter(lambda x: isinstance(x, QTabWidget), [parent_tab_widget.widget(i) for i in range(parent_tab_widget.count())]))
        assert isIncluded(tab_widget, expected_groups_commands[1]), "expected name is not included"
