import click
import pytest
import os

import clickqt.widgets
from clickqt.core.gui import GUI

@pytest.mark.parametrize(
    ("clickqt_type", "click_attrs"),
    [
        (clickqt.widgets.TextField, {"type":str}),
        (clickqt.widgets.FileField, {"type":click.types.File()}),
        (clickqt.widgets.FilePathField, {"type":click.types.Path()}),
    ]
)
def test_set_envvar(clickqt_type:clickqt.widgets.BaseWidget, click_attrs:dict):
    expected:str = None
    # Take one envvar, OS dependent
    envvars = ["TMPDIR", "TEMP", "TMP", "HOME"] 
    for ev in envvars:
        if (path := os.environ.get(ev)):
            expected = path
            break

    param = click.Option(param_decls=["--test"], envvar=envvars, **click_attrs)
    cli = click.Command("cli", params=[param])

    # Create type directly
    #widget: clickqt.widgets.BaseWidget = clickqt_type(otype=param.type, param=param, default=param.default, widgetsource=GUI().create_widget, com=cli)
    #assert widget.getWidgetValue() == expected, "directly"

    # clickqt creates the type
    control = clickqt.qtgui_from_click(cli)
    assert control.widget_registry[cli.name][param.name].getWidgetValue() == expected, "clickqt"
