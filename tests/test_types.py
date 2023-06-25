import click
import pytest

from tests.testutils import ClickAttrs
import clickqt.widgets
from typing import Any

@pytest.mark.parametrize(
    ("click_attrs", "expected_clickqt_type"),
    [
        (ClickAttrs.checkbox(), clickqt.widgets.CheckBox),
        (ClickAttrs.messagebox(prompt="Test"), clickqt.widgets.MessageBox),  
        (ClickAttrs.intfield(), clickqt.widgets.IntField), 
        (ClickAttrs.realfield(), clickqt.widgets.RealField), 
        (ClickAttrs.confirmation_widget(), clickqt.widgets.ConfirmationWidget),
        (ClickAttrs.textfield(), clickqt.widgets.TextField),
        (ClickAttrs.passwordfield(), clickqt.widgets.PasswordField),
        (ClickAttrs.datetime(), clickqt.widgets.DateTimeEdit),
        (ClickAttrs.uuid(), clickqt.widgets.TextField), 
        (ClickAttrs.unprocessed(), clickqt.widgets.TextField), 
        (ClickAttrs.combobox(choices=["a"]), clickqt.widgets.ComboBox), 
        (ClickAttrs.checkable_combobox(choices=["a"]), clickqt.widgets.CheckableComboBox), 
        (ClickAttrs.filefield(), clickqt.widgets.FileField), 
        (ClickAttrs.filepathfield(), clickqt.widgets.FilePathField), 
        (ClickAttrs.nvalue_widget(), clickqt.widgets.NValueWidget),
        (ClickAttrs.tuple_widget(types=(click.types.Path(),int)), clickqt.widgets.TupleWidget),
        (ClickAttrs.multi_value_widget(nargs=2), clickqt.widgets.MultiValueWidget),  
    ]
)
def test_type_assignment(click_attrs:dict, expected_clickqt_type:clickqt.widgets.BaseWidget):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])

    control = clickqt.qtgui_from_click(cli)
    assert type(control.widget_registry[cli.name][param.name]) is expected_clickqt_type, "clickqt"

@pytest.mark.parametrize(
    ("click_attrs", "value", "expected"),
    [
        (ClickAttrs.checkbox(), True, True),
        (ClickAttrs.checkbox(), 1, True),
        (ClickAttrs.checkbox(), "yes", True),
        (ClickAttrs.checkbox(), False, False),
        (ClickAttrs.checkbox(), 0, False),
        (ClickAttrs.checkbox(), "no", False),
        (ClickAttrs.intfield(), 12, 12), 
        (ClickAttrs.intfield(), -1322, -1322), 
        (ClickAttrs.intfield(), "-31", -31), 
        (ClickAttrs.realfield(), 152.31, 152.31), 
        (ClickAttrs.realfield(), -123.2, -123.2),
        (ClickAttrs.realfield(), "1.23", 1.23),
        (ClickAttrs.textfield(), "test123", "test123"),
        (ClickAttrs.passwordfield(), "abc", "abc"),
        (ClickAttrs.confirmation_widget(), "test321", "test321"),
        (ClickAttrs.messagebox(prompt="Test"), True, True),
        (ClickAttrs.messagebox(prompt="Test"), "y", True),
        (ClickAttrs.messagebox(prompt="Test"), "on", True),
        (ClickAttrs.messagebox(prompt="Test"), False, False),
        (ClickAttrs.messagebox(prompt="Test"), "n", False),
        (ClickAttrs.messagebox(prompt="Test"), "off", False),
        (ClickAttrs.combobox(choices=["A", "B", "C"]), "B", "B"), 
        (ClickAttrs.combobox(choices=["A", "B", "C"], case_sensitive=False), "b", "B"), 
        (ClickAttrs.checkable_combobox(choices=["A", "B", "C"]), ["B", "C"], ["B", "C"]), 
        (ClickAttrs.checkable_combobox(choices=["A", "B", "C"], case_sensitive=False), ["a", "c"], ["A", "C"]), 
        (ClickAttrs.filefield(), "test.abc", "test.abc"), 
        (ClickAttrs.filepathfield(), ".", "."), 
        (ClickAttrs.tuple_widget(types=(str,int)), ["s", 1], ["s", 1]),
        (ClickAttrs.multi_value_widget(nargs=3), ["a", "b", "c"], ["a", "b", "c"]),
        (ClickAttrs.nvalue_widget(type=int), [1, 2, 5], [1, 2, 5]),
        (ClickAttrs.nvalue_widget(type=(str,float)), [["a", 12.2], ["b", -873.21]], [["a", 12.2], ["b", -873.21]]),
    ]
)
def test_set_value(click_attrs:dict, value:Any, expected:Any):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])

    control = clickqt.qtgui_from_click(cli)
    control.widget_registry[cli.name][param.name].setValue(value)

    assert control.widget_registry[cli.name][param.name].getWidgetValue() == expected, "clickqt"

@pytest.mark.parametrize(
    ("click_attrs", "value", "expected"),
    [
        (ClickAttrs.checkbox(), 12, "'12' is not a valid boolean."),
        (ClickAttrs.checkbox(), "ok", "'ok' is not a valid boolean."),
        (ClickAttrs.checkbox(), "-1.0", "'-1.0' is not a valid boolean."),
        (ClickAttrs.intfield(), -2.12, "'-2.12' is not a valid integer."),
        (ClickAttrs.intfield(), "True", "'True' is not a valid integer."),
        (ClickAttrs.intfield(), "-1.0", "'-1.0' is not a valid integer."),
        (ClickAttrs.realfield(), "no", "'no' is not a valid float."),
        (ClickAttrs.combobox(choices=["A", "B"]), "b", "'b' is not one of 'A', 'B'."), 
        (ClickAttrs.combobox(choices=["A", "B"], case_sensitive=False), "C", "'C' is not one of 'A', 'B'."), 
        (ClickAttrs.checkable_combobox(choices=["A", "B", "C"]), ["b", "C"], "'b' is not one of 'A', 'B', 'C'."), 
        (ClickAttrs.checkable_combobox(choices=["A", "B", "C"], case_sensitive=False), ["a", "t", "c"], "'t' is not one of 'A', 'B', 'C'."),
        (ClickAttrs.multi_value_widget(nargs=3, type=int), ["1", 2, 3.2], "'3.2' is not a valid integer."),
        (ClickAttrs.multi_value_widget(nargs=2, type=float), ["yes", "y"], "'yes' is not a valid float."), # First wrong value fails the test
        (ClickAttrs.tuple_widget(types=(str,int)), ["s", 12.3], "'12.3' is not a valid integer."),
        (ClickAttrs.nvalue_widget(type=(str,float)), [["a", "set"], ["b", "t"]], "'set' is not a valid float."), # First wrong value fails the test
    ]
)
def test_set_value_fail(click_attrs:dict, value:Any, expected:Any):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])

    control = clickqt.qtgui_from_click(cli)
    with pytest.raises(click.exceptions.BadParameter) as exc_info:
        control.widget_registry[cli.name][param.name].setValue(value)

    assert expected in exc_info.value.message, "clickqt"
