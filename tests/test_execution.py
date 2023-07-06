import click
from click.testing import CliRunner
import pytest

from tests.testutils import ClickAttrs, clcoancl, raise_
from PySide6.QtWidgets import QMessageBox, QInputDialog, QApplication
from pytest import MonkeyPatch
import clickqt.widgets
from clickqt.core.error import ClickQtError
from typing import Any
import time


def prepare_execution(monkeypatch:MonkeyPatch, value:Any, widget:clickqt.widgets.BaseWidget) -> tuple[str, str|None]:
    if isinstance(widget, clickqt.widgets.MessageBox):
        # Mock the QMessageBox.information-function
        # User clicked on button "Yes" or "No"
        monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.Yes if value else QMessageBox.No)
    elif isinstance(widget, clickqt.widgets.FileField) and value == "-" and "r" in widget.type.mode:
        monkeypatch.setattr(QInputDialog, "getMultiLineText", lambda *args: (value, True)) # value, ok

    args:str = ""

    if widget.param.multiple:
        def reduce(value) -> str:
            arg_str = "--p="
            for v in value:
                if isinstance(v, list):
                    return reduce(v)
                elif str(v) != "":
                    arg_str += str(v) + " "
            return arg_str if arg_str != "--p=" else ""
        for v in value:
            if isinstance(v, list):
                args += reduce(v)
            else:
                args += f"--p={str(v)} "
    elif isinstance(widget, clickqt.widgets.MultiWidget):
        args = "--p=" if len(value) > 0 else ""
        for v in value:
            if str(v) != "":
                args += str(v) + " "
            else: # Don't pass an argument string if any child is empty
               args = ""
               break 
    elif not isinstance(widget, clickqt.widgets.MessageBox):
        if isinstance(value, str) and value == "":
            args = ""
        else:
            args = f"--p={str(value)}"

    input = None if not isinstance(widget, clickqt.widgets.MessageBox) else \
            "y" if value else "n"
    
    return (args, input)


@pytest.mark.parametrize(
    ("click_attrs", "value", "error"),
    [
        (ClickAttrs.checkbox(), False, ClickQtError()),
        (ClickAttrs.checkbox(), True, ClickQtError()),
        (ClickAttrs.messagebox(prompt="Test"), False, ClickQtError()),
        (ClickAttrs.messagebox(prompt="Test"), True, ClickQtError()),
        (ClickAttrs.intfield(), 12, ClickQtError()),
        (ClickAttrs.realfield(), -123.2, ClickQtError()),
        (ClickAttrs.intrange(max=2, clamp=True), 5, ClickQtError()),
        (ClickAttrs.floatrange(min=2.5, clamp=True), -1, ClickQtError()),
        (ClickAttrs.textfield(), "test123", ClickQtError()),
        (ClickAttrs.passwordfield(), "abc", ClickQtError()),
        (ClickAttrs.confirmation_widget(), "test321", ClickQtError()),
        (ClickAttrs.combobox(choices=["A", "B", "C"], case_sensitive=False), "b", ClickQtError()),
        (ClickAttrs.checkable_combobox(choices=["A", "B", "C"]), [], ClickQtError()),
        (ClickAttrs.checkable_combobox(choices=["A", "B", "C"]), ["B", "C"], ClickQtError()), 
        (ClickAttrs.datetime(formats=["%d-%m-%Y"]), "23-06-2023", ClickQtError()),
        (ClickAttrs.filefield(), ".gitignore", ClickQtError()), 
        (ClickAttrs.filefield(type_dict={"mode":"rb"}), "-", ClickQtError()), 
        (ClickAttrs.filefield(type_dict={"mode":"w"}), "-", ClickQtError()), 
        (ClickAttrs.filefield(type_dict={"mode":"wb"}), "-", ClickQtError()), 
        (ClickAttrs.filepathfield(), ".", ClickQtError()),
        (ClickAttrs.tuple_widget(types=()), [], ClickQtError()),
        (ClickAttrs.tuple_widget(types=(str, int, float)), ("t", 1, -2.), ClickQtError()),
        (ClickAttrs.multi_value_widget(nargs=3, type=float), [1.2, "-3.5", -2], ClickQtError()),
        (ClickAttrs.multi_value_widget(nargs=2), ["", ""], ClickQtError()),
        (ClickAttrs.nvalue_widget(type=(str, int)), [["a", 12], ["c", -1]], ClickQtError()),
        (ClickAttrs.nvalue_widget(type=(str, int)), [], ClickQtError()),

        # Aborted error
        (ClickAttrs.messagebox(prompt="Test", callback=lambda ctx, param, value: ctx.abort()), False, 
            ClickQtError(ClickQtError.ErrorType.ABORTED_ERROR)),
        (ClickAttrs.nvalue_widget(type=(str, int), callback=lambda ctx, param, value: ctx.abort()), [["ab", 12]], 
            ClickQtError(ClickQtError.ErrorType.ABORTED_ERROR)), 
        # Exit error
        (ClickAttrs.textfield(callback=lambda ctx, param, value: ctx.exit(1)), "abc", ClickQtError(ClickQtError.ErrorType.EXIT_ERROR)),
        (ClickAttrs.nvalue_widget(type=(int, str), callback=lambda ctx, param, value: ctx.exit(1)), [[2, "a"]], ClickQtError(ClickQtError.ErrorType.EXIT_ERROR)),
        # Converting error (invalid file/path)
        (ClickAttrs.filefield(), "invalid_file", ClickQtError(ClickQtError.ErrorType.CONVERTING_ERROR)), 
        (ClickAttrs.filepathfield(type_dict={"exists":True}), "invalid_path", ClickQtError(ClickQtError.ErrorType.CONVERTING_ERROR)), 
        (ClickAttrs.nvalue_widget(type=(click.types.File(), int)), [[".gitignore", 12], ["invalid_file", -1]], 
            ClickQtError(ClickQtError.ErrorType.CONVERTING_ERROR)),
        # Processing error (Callback raises an exception)
        (ClickAttrs.intfield(callback=lambda ctx,param,value: raise_(click.exceptions.BadParameter("..."))), -3, 
            ClickQtError(ClickQtError.ErrorType.PROCESSING_VALUE_ERROR)), 
        (ClickAttrs.nvalue_widget(type=(int, str), callback=lambda ctx,param,value: raise_(click.exceptions.BadParameter("...")) if value[0] != (12, "test") else value), 
            [[11, "test"], [231, "abc"]], ClickQtError(ClickQtError.ErrorType.PROCESSING_VALUE_ERROR)), 
        # Required error (Required param not provided)
        (ClickAttrs.textfield(required=True), "", ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR)),
        (ClickAttrs.checkable_combobox(choices=["A", "B", "C"], required=True), [], ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR)),
        (ClickAttrs.multi_value_widget(nargs=2, required=True), ["", ""], ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR)),
        (ClickAttrs.nvalue_widget(type=(str, str), required=True), [["", ""]], ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR)),
        (ClickAttrs.nvalue_widget(type=(str, str), required=True), [], ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR)),

        # With default
        (ClickAttrs.textfield(default=""), "", ClickQtError()), # Empty string is accepted
        (ClickAttrs.checkable_combobox(choices=["A", "B", "C"], default=["B"]), [], ClickQtError()),
        (ClickAttrs.multi_value_widget(nargs=2, default=["A", "B"]), ["", ""], ClickQtError()),
    ]
)
def test_execution(monkeypatch:MonkeyPatch, runner:CliRunner, click_attrs:dict, value:Any, error:ClickQtError):
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

    args, input = prepare_execution(monkeypatch, value, widget)
    click_res = runner.invoke(cli, args, input, standalone_mode=False if error.type != ClickQtError.ErrorType.EXIT_ERROR else True) # See click/core.py#1082
    val, err = widget.getValue()

    assert err.type == error.type

    if callable(val):
        val, err = val()

    # First compare the value from 'widget.getValue()' with the click result
    # then the clickqt result (run_button clicked) with the click result
    for i in range(2):
        if not isinstance(widget, clickqt.widgets.FileField):
            assert val == click_res.return_value
        else: # IOWrapper-objects can't be compared
            closest_common_ancestor_class = clcoancl(type(val), type(click_res.return_value))
            assert closest_common_ancestor_class not in {None, object}
        
        if i == 0:
            assert err.type == error.type
            if error.type == ClickQtError.ErrorType.ABORTED_ERROR:
                assert type(click_res.exception) is click.exceptions.Abort
            elif error.type == ClickQtError.ErrorType.EXIT_ERROR:
                assert type(click_res.exception) is SystemExit # Not click.exceptions.Exit, see click/core.py#1082
            elif error.type == ClickQtError.ErrorType.REQUIRED_ERROR:
                assert type(click_res.exception) is click.exceptions.MissingParameter
            elif error.type in {ClickQtError.ErrorType.CONVERTING_ERROR, ClickQtError.ErrorType.PROCESSING_VALUE_ERROR}:
                assert type(click_res.exception) is click.exceptions.BadParameter
            else:
                assert click_res.exception is None

            clickqt_res = None # Reset the stored click result
            control.gui.run_button.click()
            for i in range(10):  # Wait for worker thread to finish the execution
                QApplication.processEvents()
                time.sleep(0.001)
            val = clickqt_res
    