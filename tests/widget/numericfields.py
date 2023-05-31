import click
import PySide6.QtCore as QtCore
import pytestqt.qtbot as qtbot
from clickqt.widgets.numericfields import IntField
from clickqt.core.error import ClickQtError
from tests.testutils import keystrokes

def test_intfield(qtbot:qtbot.QtBot):
    option = click.Option(["--testintopt"], default=1)
    ifield = IntField(option.to_info_dict())

    val, err = ifield.getValue()
    assert val == 1 and err == ClickQtError.ErrorType.NO_ERROR
    keystrokes(ifield.widget, qtbot, "23")
    val, err = ifield.getValue()
    assert val == 231 and err == ClickQtError.ErrorType.NO_ERROR
    qtbot.keyClick(ifield.widget, QtCore.Qt.Key.Key_Backspace)
    qtbot.keyClick(ifield.widget, QtCore.Qt.Key.Key_Backspace)
    val, err = ifield.getValue()
    assert val == 1 and err == ClickQtError.ErrorType.NO_ERROR
    qtbot.keyClick(ifield.widget, QtCore.Qt.Key.Key_Minus)
    val, err = ifield.getValue()
    assert val == -1 and err == ClickQtError.ErrorType.NO_ERROR
    qtbot.keyClick(ifield.widget, QtCore.Qt.Key.Key_Period)
    val, err = ifield.getValue()
    assert val == -1 and err == ClickQtError.ErrorType.NO_ERROR
