import click
import pytest

from tests.testutils import ClickAttrs, raise_
import clickqt.widgets
from typing import Any
from PySide6.QtCore import QEvent


@pytest.mark.parametrize(
    ("click_attrs", "invalid_value", "valid_value"),
    [
        (ClickAttrs.intfield(callback=lambda ctx,param,value: raise_(Exception("...")) if value < 5 else value), 0, 10),
        (ClickAttrs.filepathfield(type_dict={"exists":True}), "invalid_path", "tests"),
        (ClickAttrs.tuple_widget(types=(str, float), callback=lambda ctx,param,value: raise_(Exception("...")) if value[0] != "abc" else value), ["a", 0], ["abc", 2.2]),
        (ClickAttrs.multi_value_widget(nargs=3, type=int, callback=lambda ctx,param,value: raise_(Exception("...")) if value != (0, 1, 2) else value), [0, 0, 0], [0, 1, 2]),
        (ClickAttrs.nvalue_widget(callback=lambda ctx,param,value: raise_(Exception("...")) if len(value) == 0 else value), [], ["abc"]),
    ]
)
def test_focus_out_validation(click_attrs:dict, invalid_value:Any, valid_value:Any):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])
    
    control = clickqt.qtgui_from_click(cli)

    control.widget_registry[cli.name][param.name].setValue(invalid_value)
    control.widget_registry[cli.name][param.name].focus_out_validator.eventFilter(control.widget_registry[cli.name][param.name].widget, QEvent(QEvent.Type.FocusOut))
    red_border = lambda widget: f"QWidget#{param.name}{{ border: 1px solid red }}" in widget.styleSheet()
    if isinstance(control.widget_registry[cli.name][param.name], clickqt.widgets.MultiWidget):
        for child in control.widget_registry[cli.name][param.name].children:
            assert red_border(child.widget)
    else:
        assert red_border(control.widget_registry[cli.name][param.name].widget)

    control.widget_registry[cli.name][param.name].setValue(valid_value)
    control.widget_registry[cli.name][param.name].focus_out_validator.eventFilter(control.widget_registry[cli.name][param.name].widget, QEvent(QEvent.Type.FocusOut))
    normal_border = lambda widget: f"QWidget#{param.name}{{ }}" == widget.styleSheet()
    if isinstance(control.widget_registry[cli.name][param.name], clickqt.widgets.MultiWidget):
        for child in control.widget_registry[cli.name][param.name].children:
            assert normal_border(child.widget)
    else:
        assert normal_border(control.widget_registry[cli.name][param.name].widget)
