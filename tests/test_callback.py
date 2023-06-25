import click
import pytest

from tests.testutils import ClickAttrs
import clickqt.widgets
from clickqt.core.error import ClickQtError
from typing import Any


@pytest.mark.parametrize(
    ("click_attrs", "value", "expected"),
    [
        (ClickAttrs.checkbox(callback=lambda ctx,param,value: not value), True, False),
        (ClickAttrs.intfield(callback=lambda a,b,value: value-1), 12, 11),
        (ClickAttrs.realfield(callback=lambda a,b,value: value+1.5), 10.5, 12), 
        (ClickAttrs.realfield(callback=lambda a,b,value: None), -312.2, None), 
        (ClickAttrs.realfield(callback=lambda a,b,value: "test"), 14.2, "test"), # Return type can be completely different
        (ClickAttrs.nvalue_widget(type=float, callback=lambda a,b,value: 1), [14.2, -2.3], 1),
        (ClickAttrs.tuple_widget(types=(int, str), callback=lambda a,b,value: [value[0]+5, "test"]), [10, "10"], [15, "test"]),
        (ClickAttrs.multi_value_widget(nargs=2, type=int, callback=lambda a,b,value: [value[0]+5, value[1]-5]), [10, 10], [15, 5]),
    ]
)
def test_set_value(click_attrs:dict, value:Any, expected:Any):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])
    
    control = clickqt.qtgui_from_click(cli)
    control.widget_registry[cli.name][param.name].setValue(value)
    val, err = control.widget_registry[cli.name][param.name].getValue()

    assert val == expected and err.type == ClickQtError.ErrorType.NO_ERROR, "clickqt"

