import click
import clickqt
import PySide6.QtCore as QtCore
import pytestqt.qtbot as qtbot
from clickqt.core.error import ClickQtError
from clickqt.widgets.checkbox import CheckBox


def test_checkbox(qtbot:qtbot.QtBot):
    option = click.Option(["--testboolopt"], default=True)
    command = click.Command("test", params=[option])
    cb = CheckBox(option, com=command)
    checkbox_pos = QtCore.QPoint(2,cb.widget.height()/2)
    
    val, err = cb.getValue()
    assert val and err.type == ClickQtError.ErrorType.NO_ERROR
    qtbot.mouseClick(cb.widget, QtCore.Qt.MouseButton.LeftButton, pos=checkbox_pos)
    val, err = cb.getValue()
    assert not val and err.type == ClickQtError.ErrorType.NO_ERROR
    qtbot.mouseClick(cb.widget, QtCore.Qt.MouseButton.LeftButton, pos=checkbox_pos)
    val, err = cb.getValue()
    assert val and err.type == ClickQtError.ErrorType.NO_ERROR

def test_gui_checkbox():
    expected:bool = True

    @click.command()
    @click.option("--verbose", default=expected)
    def dist(verbose):
        assert isinstance(verbose, bool)
        assert verbose == expected

    control = clickqt.qtgui_from_click(dist)
    run_button = control.gui.run_button

    # Check if default value was set correctly
    run_button.click() 

    for _ in range(2):
        expected = not expected
        control.widget_registry[dist.name][dist.params[0].name].setValue(expected)
        run_button.click() 
    
    # Wrong type does not change the widget value
    control.widget_registry[dist.name][dist.params[0].name].setValue(0)
    run_button.click()