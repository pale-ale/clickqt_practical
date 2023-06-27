import click
import pytest

from tests.testutils import ClickAttrs, raise_
import clickqt.widgets


@pytest.mark.parametrize(
    ("click_attrs"),
    [
        (ClickAttrs.intfield(callback=lambda ctx,param,value: raise_(Exception("...")))),
    ]
)
def test_focus_out_validation(click_attrs:dict):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])
    
    control = clickqt.qtgui_from_click(cli)
    control.gui.window.show()
    control.widget_registry[cli.name][param.name].widget.setFocus()
    control.gui.window.setFocus()

    assert "border: 1px solid red" in control.widget_registry[cli.name][param.name].widget.styleSheet()