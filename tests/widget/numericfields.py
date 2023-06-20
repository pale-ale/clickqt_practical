import click
import clickqt
import PySide6.QtCore as QtCore
from PySide6.QtWidgets import QTabWidget, QWidget, QSpinBox, QPushButton
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

    gui = clickqt.qtgui_from_click(dist).gui

    tab_window:QWidget = gui.main_tab.findChild(QWidget)
    assert tab_window is not None
    count:QSpinBox = tab_window.findChild(QWidget).findChild(QSpinBox)
    assert count is not None

    gui.run_button.click() # Check if default value was set correctly

    for _ in range(5):
        expected = random.randint(-10000, 10000)
        count.setValue(expected)
        gui.run_button.click() 
