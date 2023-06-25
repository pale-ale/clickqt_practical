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
        (ClickAttrs.checkbox(callback=lambda a,b,value: not value), False, True),
        (ClickAttrs.intfield(callback=lambda a,b,value: value-1), 12, 11), 
    ]
)
def test_set_value(click_attrs:dict, value:Any, expected:Any):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])
    
    control = clickqt.qtgui_from_click(cli)
    control.widget_registry[cli.name][param.name].setValue(value)
    val, err = control.widget_registry[cli.name][param.name].getValue()

    assert val == expected and err.type == ClickQtError.ErrorType.NO_ERROR, "clickqt"

