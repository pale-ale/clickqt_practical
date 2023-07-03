import click
from click.testing import CliRunner
import pytest

from tests.testutils import ClickAttrs, clcoancl
from PySide6.QtWidgets import QMessageBox, QInputDialog
from pytest import MonkeyPatch
import clickqt.widgets
from clickqt.core.error import ClickQtError
from typing import Any


def prepare_execution(monkeypatch:MonkeyPatch, value:Any, widget:clickqt.widgets.BaseWidget, param:click.Parameter) -> tuple[str, str|None]:
    if isinstance(widget, clickqt.widgets.MessageBox):
        # Mock the QMessageBox.information-function
        # User clicked on button "Yes" or "No"
        monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.Yes if value else QMessageBox.No)
    elif isinstance(widget, clickqt.widgets.FileField) and value == "-" and "r" in param.type.mode:
        monkeypatch.setattr(QInputDialog, "getMultiLineText", lambda *args: (value, True)) # value, ok

    args:str = ""

    if param.multiple:
        def reduce(value) -> str:
            arg_str = "--p="
            for v in value:
                if isinstance(v, list):
                    return reduce(v)
                else:
                    arg_str += str(v) + " "
            return arg_str
        for v in value:
            if isinstance(v, list):
                args += reduce(v)
            else:
                args += f"--p={str(v)} "
    elif isinstance(widget, clickqt.widgets.MultiWidget):
        args = "--p="
        for v in value:
            args += str(v) + " "
    elif not isinstance(widget, clickqt.widgets.MessageBox):
        args = f"--p={str(value)}"

    input = None if not isinstance(widget, clickqt.widgets.MessageBox) else \
            "y" if value else "n"
    
    return (args, input)


@pytest.mark.parametrize(
    ("click_attrs", "value"),
    [
        (ClickAttrs.checkbox(), False),
        (ClickAttrs.checkbox(), True),
        (ClickAttrs.messagebox(prompt="Test"), False),
        (ClickAttrs.messagebox(prompt="Test"), True),
        (ClickAttrs.intfield(), 12),
        (ClickAttrs.realfield(), -123.2),
        (ClickAttrs.intrange(max=2, clamp=True), 5),
        (ClickAttrs.floatrange(min=2.5, clamp=True), -1),
        (ClickAttrs.textfield(), "test123"),
        (ClickAttrs.passwordfield(), "abc"),
        (ClickAttrs.confirmation_widget(), "test321"),
        (ClickAttrs.combobox(choices=["A", "B", "C"], case_sensitive=False), "b"),
        (ClickAttrs.checkable_combobox(choices=["A", "B", "C"]), ["B", "C"]), 
        (ClickAttrs.datetime(formats=["%d-%m-%Y"]), "23-06-2023"),
        (ClickAttrs.filefield(), ".gitignore"), 
        (ClickAttrs.filefield(type_dict={"mode":"rb"}), "-"), 
        (ClickAttrs.filefield(type_dict={"mode":"w"}), "-"), 
        (ClickAttrs.filefield(type_dict={"mode":"wb"}), "-"), 
        (ClickAttrs.filepathfield(), "."),
        (ClickAttrs.tuple_widget(types=(str, int, float)), ("t", 1, -2.)),
        (ClickAttrs.multi_value_widget(nargs=3, type=float), [1.2, "-3.5", -2]),
        (ClickAttrs.nvalue_widget(type=(str, int)), [["a", 12], ["c", -1]]),
    ]
)
def test_execution(monkeypatch:MonkeyPatch, runner:CliRunner, click_attrs:dict, value:Any):
    clickqt_res:Any = None

    def callback(p):
        nonlocal clickqt_res
        if clickqt_res is None:
            clickqt_res = p
        return p

    param = click.Option(param_decls=["--p"], **click_attrs)
    cli = click.Command("cli", params=[param], callback=callback)
    
    control = clickqt.qtgui_from_click(cli)
    widget = control.widget_registry[cli.name][param.name]

    widget.setValue(value)

    args, input = prepare_execution(monkeypatch, value, widget, param)

    click_res = runner.invoke(cli, args, input, standalone_mode=False)
    val, err = widget.getValue()

    assert err.type == ClickQtError.ErrorType.NO_ERROR    

    if callable(val):
        val, err = val()

    # First compare the value from 'widget.getValue()' with the click result
    # then the clickqt result (run_button clicked) with the click result
    for i in range(2):
        if not isinstance(widget, clickqt.widgets.FileField):  
            assert val == click_res.return_value
        else: # IOWrapper-objects can't be compared
            closest_common_ancestor_class = clcoancl(type(val), type(click_res.return_value))
            assert closest_common_ancestor_class is not None and closest_common_ancestor_class is not object
        
        if i == 0:
            assert err.type == ClickQtError.ErrorType.NO_ERROR    
            assert click_res.exception is None

            clickqt_res = None # Reset the stored click result
            control.gui.run_button.click()
            val = clickqt_res
    