import click
import clickqt
from clickqt.widgets.messagebox import MessageBox
from PySide6.QtWidgets import QMessageBox
from pytest import MonkeyPatch
from clickqt.core.error import ClickQtError

def test_gui_messagebox(monkeypatch: MonkeyPatch):
    @click.command()
    @click.confirmation_option(prompt='Are you sure?')
    def dist():
        pass

    control = clickqt.qtgui_from_click(dist)
    messagebox_widget = control.widget_registry[dist.name][dist.params[0].name]
    assert isinstance(messagebox_widget, MessageBox)

    # Mock the QMessageBox.information-function
    # User clicked on button "Yes"
    monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.Yes)
    value, err = messagebox_widget.getValue() # Default callback returns "None" as value, see click/decorators.py#323
    assert value == None and err.type == ClickQtError.ErrorType.NO_ERROR
    
    # User clicked on button "No"
    monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.No)
    value, err = messagebox_widget.getValue() # User aborted so getValue() returns "None" as value
    assert value == None and err.type == ClickQtError.ErrorType.ABORTED_ERROR