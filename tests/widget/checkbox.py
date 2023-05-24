import click
import PySide6.QtCore as QtCore
import pytestqt.qtbot as qtbot
from clickqt.core.error import ClickQtError
from clickqt.widgets.checkbox import CheckBox


def test_checkbox(qtbot:qtbot.QtBot):
    option = click.Option(["--testboolopt"], default=True)
    cb = CheckBox(option.to_info_dict())
    checkbox_pos = QtCore.QPoint(2,cb.widget.height()/2)
    
    val, err = cb.getValue()
    assert val and err == ClickQtError.NO_ERROR
    qtbot.mouseClick(cb.widget, QtCore.Qt.MouseButton.LeftButton, pos=checkbox_pos)
    val, err = cb.getValue()
    assert not val and err == ClickQtError.NO_ERROR
    qtbot.mouseClick(cb.widget, QtCore.Qt.MouseButton.LeftButton, pos=checkbox_pos)
    val, err = cb.getValue()
    assert val and err == ClickQtError.NO_ERROR
