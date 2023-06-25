import click
import pytest

import clickqt.widgets
from clickqt.core.gui import GUI
from typing import Any

@pytest.mark.parametrize(
    ("attrs", "expected_clickqt_type"),
    [
        ({"type":bool}, clickqt.widgets.CheckBox),
        ({"type":bool, "is_flag":True, "prompt": "Test"}, clickqt.widgets.MessageBox),  
        ({"type":int}, clickqt.widgets.IntField), 
        ({"type":int, "confirmation_prompt":True}, clickqt.widgets.ConfirmationWidget),
        ({"type":float}, clickqt.widgets.RealField), 
        ({"type":float, "nargs":3}, clickqt.widgets.MultiValueWidget),
        ({"type":float, "multiple":True}, clickqt.widgets.NValueWidget),
        ({"type":str}, clickqt.widgets.TextField),
        ({"type":str, "hide_input":True}, clickqt.widgets.PasswordField),
        ({"type":str, "confirmation_prompt":True}, clickqt.widgets.ConfirmationWidget),
        ({"type":str, "nargs":2}, clickqt.widgets.MultiValueWidget), 
        ({"type":click.types.UUID}, clickqt.widgets.TextField), 
        ({"type":click.types.UNPROCESSED}, clickqt.widgets.TextField), 
        ({"type":click.types.Choice([])}, clickqt.widgets.ComboBox), 
        ({"type":click.types.Choice([]), "multiple":True}, clickqt.widgets.CheckableComboBox), 
        ({"type":click.types.File()}, clickqt.widgets.FileField), 
        ({"type":click.types.Path()}, clickqt.widgets.FilePathField), 
        ({"type":()}, clickqt.widgets.TupleWidget), 
    ]
)
def test_type_assignment(attrs:dict, expected_clickqt_type:clickqt.widgets.BaseWidget):
    param = click.Option(param_decls=["--test"], **attrs)
    cli = click.Command("cli", params=[param])

    # Create type directly, perfect type match
    #gui = GUI()
    #assert type(gui.create_widget(otype=param.type, param=param, default=param.default, widgetsource=gui.create_widget, com=cli)) is expected_clickqt_type, "directly"

    # clickqt creates the type, perfect type match
    control = clickqt.qtgui_from_click(cli)
    assert type(control.widget_registry[cli.name][param.name]) is expected_clickqt_type, "clickqt"

@pytest.mark.parametrize(
    ("clickqt_type", "click_attrs", "value", "expected"),
    [
        (clickqt.widgets.CheckBox, {"type":bool}, True, True),
        (clickqt.widgets.CheckBox, {"type":bool}, 1, True),
        (clickqt.widgets.CheckBox, {"type":bool}, "yes", True),
        (clickqt.widgets.CheckBox, {"type":bool}, False, False),
        (clickqt.widgets.CheckBox, {"type":bool}, 0, False),
        (clickqt.widgets.CheckBox, {"type":bool}, "no", False),
        (clickqt.widgets.IntField, {"type":int}, 12, 12), 
        (clickqt.widgets.IntField, {"type":int}, -1322, -1322), 
        (clickqt.widgets.IntField, {"type":int}, "-31", -31), 
        (clickqt.widgets.RealField, {"type":float}, 152.31, 152.31), 
        (clickqt.widgets.RealField, {"type":float}, -123.2, -123.2),
        (clickqt.widgets.RealField, {"type":float}, "1.23", 1.23),
        (clickqt.widgets.TextField, {}, "test123", "test123"),
        (clickqt.widgets.PasswordField, {"hide_input": True}, "abc", "abc"),
        (clickqt.widgets.ConfirmationWidget, {"confirmation_prompt": True}, "test321", "test321"),
        (clickqt.widgets.MessageBox, {"is_flag": True, "prompt": "Test"}, True, True),
        (clickqt.widgets.MessageBox, {"is_flag": True, "prompt": "Test"}, "y", True),
        (clickqt.widgets.MessageBox, {"is_flag": True, "prompt": "Test"}, "on", True),
        (clickqt.widgets.MessageBox, {"is_flag": True, "prompt": "Test"}, False, False),
        (clickqt.widgets.MessageBox, {"is_flag": True, "prompt": "Test"}, "n", False),
        (clickqt.widgets.MessageBox, {"is_flag": True, "prompt": "Test"}, "off", False),
        (clickqt.widgets.ComboBox, {"type": click.types.Choice(["A", "B", "C"])}, "B", "B"), 
        (clickqt.widgets.ComboBox, {"type": click.types.Choice(["A", "B", "C"], case_sensitive=False)}, "b", "B"), 
        (clickqt.widgets.CheckableComboBox, {"type": click.types.Choice(["A", "B", "C"]), "multiple":True}, ["B", "C"], ["B", "C"]), 
        (clickqt.widgets.CheckableComboBox, {"type": click.types.Choice(["A", "B", "C"], case_sensitive=False), "multiple":True}, ["a", "c"], ["A", "C"]), 
        (clickqt.widgets.FileField, {"type": click.types.File()}, "README.md", "README.md"), 
        (clickqt.widgets.FilePathField, {"type": click.types.Path()}, ".", "."), 
        (clickqt.widgets.TupleWidget, {"type": (str, int)}, ["s", 1], ["s", 1]),
        (clickqt.widgets.MultiValueWidget, {"nargs": 3}, ["a", "b", "c"], ["a", "b", "c"]),
        (clickqt.widgets.NValueWidget, {"type":int, "multiple":True}, [1, 2, 5], [1, 2, 5]),
        (clickqt.widgets.NValueWidget, {"type":(str, float), "multiple":True}, [["a", 12.2], ["b", -873.21]], [["a", 12.2], ["b", -873.21]]),
    ]
)
def test_set_value(clickqt_type:clickqt.widgets.BaseWidget, click_attrs:dict, value:Any, expected:Any):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])
    
    # Create type directly
    #widget: clickqt.widgets.BaseWidget = clickqt_type(otype=param.type, param=param, default=param.default, widgetsource=GUI().create_widget, com=cli)
    #widget.setValue(value)

    #assert widget.getWidgetValue() == expected, "directly"

    # clickqt creates the type
    control = clickqt.qtgui_from_click(cli)
    control.widget_registry[cli.name][param.name].setValue(value)

    assert control.widget_registry[cli.name][param.name].getWidgetValue() == expected, "clickqt"

@pytest.mark.parametrize(
    ("clickqt_type", "click_attrs", "value", "expected"),
    [
        (clickqt.widgets.CheckBox, {"type":bool}, 12, "'12' is not a valid boolean."),
        (clickqt.widgets.CheckBox, {"type":bool}, "ok", "'ok' is not a valid boolean."),
        (clickqt.widgets.CheckBox, {"type":bool}, "-1.0", "'-1.0' is not a valid boolean."),
        (clickqt.widgets.IntField, {"type":int}, -2.12, "'-2.12' is not a valid integer."),
        (clickqt.widgets.IntField, {"type":int}, "True", "'True' is not a valid integer."),
        (clickqt.widgets.IntField, {"type":int}, "-1.0", "'-1.0' is not a valid integer."),
        (clickqt.widgets.RealField, {"type":float}, "no", "'no' is not a valid float."),
        (clickqt.widgets.ComboBox, {"type": click.types.Choice(["A", "B"])}, "b", "'b' is not one of 'A', 'B'."), 
        (clickqt.widgets.ComboBox, {"type": click.types.Choice(["A", "B"], case_sensitive=False)}, "C", "'C' is not one of 'A', 'B'."), 
        (clickqt.widgets.CheckableComboBox, {"type": click.types.Choice(["A", "B", "C"]), "multiple":True}, ["b", "C"], "'b' is not one of 'A', 'B', 'C'."), 
        (clickqt.widgets.CheckableComboBox, {"type": click.types.Choice(["A", "B", "C"], case_sensitive=False), "multiple":True}, ["a", "t", "c"], "'t' is not one of 'A', 'B', 'C'."),
        (clickqt.widgets.MultiValueWidget, {"type":int, "nargs": 3}, ["1", 2, 3.2], "'3.2' is not a valid integer."),
        (clickqt.widgets.MultiValueWidget, {"type":float, "nargs": 2}, ["yes", "y"], "'yes' is not a valid float."), # First wrong value fails the test
        (clickqt.widgets.TupleWidget, {"type": (str, int)}, ["s", 12.3], "'12.3' is not a valid integer."),
        (clickqt.widgets.NValueWidget, {"type":(str, float), "multiple":True}, [["a", "set"], ["b", "t"]], "'set' is not a valid float."), # First wrong value fails the test
    ]
)
def test_set_value_fail(clickqt_type:clickqt.widgets.BaseWidget, click_attrs:dict, value:Any, expected:Any):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])

    # Create type directly
    #widget: clickqt.widgets.BaseWidget = clickqt_type(otype=param.type, param=param, default=param.default, widgetsource=GUI().create_widget, com=cli)
    #with pytest.raises(click.exceptions.BadParameter) as exc_info:
    #   widget.setValue(value)

    #assert expected in exc_info.value.message, "directly"

    # clickqt creates the type
    control = clickqt.qtgui_from_click(cli)
    with pytest.raises(click.exceptions.BadParameter) as exc_info:
        control.widget_registry[cli.name][param.name].setValue(value)

    assert expected in exc_info.value.message, "clickqt"
