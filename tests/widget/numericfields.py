import click
import clickqt
import PySide6.QtCore as QtCore
import pytestqt.qtbot as qtbot
from clickqt.widgets.numericfields import IntField
from clickqt.core.error import ClickQtError
from tests.testutils import keystrokes
import random

def test_intfield(qtbot:qtbot.QtBot):
    option = click.Option(["--testintopt"], default=1)
    command = click.Command("test", params=[option])
    ifield = IntField(option, com=command)

    val, err = ifield.getValue()
    assert val == 1 and err.type == ClickQtError.ErrorType.NO_ERROR
    keystrokes(ifield.widget, qtbot, "23")
    val, err = ifield.getValue()
    assert val == 231 and err.type == ClickQtError.ErrorType.NO_ERROR
    qtbot.keyClick(ifield.widget, QtCore.Qt.Key.Key_Backspace)
    qtbot.keyClick(ifield.widget, QtCore.Qt.Key.Key_Backspace)
    val, err = ifield.getValue()
    assert val == 1 and err.type == ClickQtError.ErrorType.NO_ERROR
    qtbot.keyClick(ifield.widget, QtCore.Qt.Key.Key_Minus)
    val, err = ifield.getValue()
    assert val == -1 and err.type == ClickQtError.ErrorType.NO_ERROR
    qtbot.keyClick(ifield.widget, QtCore.Qt.Key.Key_Period)
    val, err = ifield.getValue()
    assert val == -1 and err.type == ClickQtError.ErrorType.NO_ERROR

def test_gui_intfield():
    expected:int = 1

    @click.command()
    @click.option("--count", default=expected)
    def dist(count):
        assert isinstance(count, int)
        assert count == expected

    control = clickqt.qtgui_from_click(dist)
    run_button = control.gui.run_button
    int_field_widget = control.widget_registry[dist.name][dist.params[0].name]
    assert isinstance(int_field_widget, IntField)
    # Check if default value was set correctly
    run_button.click() 

    for _ in range(5):
        expected = random.randint(-10000, 10000)
        int_field_widget.setValue(expected)
        run_button.click() 

    # Wrong type does not change the widget value
    int_field_widget.setValue(str(expected+12))
    run_button.click() 
