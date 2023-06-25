import click
import pytest
import os

import clickqt.widgets
from clickqt.core.gui import GUI

@pytest.mark.parametrize(
    ("clickqt_type", "click_attrs", "envvar_values", "expected"),
    [
        (clickqt.widgets.TextField, {"type":str}, "test123", "test123"),
        (clickqt.widgets.TextField, {"type":str}, ["test1", "test2"], os.path.pathsep.join(["test1", "test2"])),
        (clickqt.widgets.FileField, {"type":click.types.File()}, "test", "test"),
        (clickqt.widgets.FileField, {"type":click.types.File()}, ["test1", "test2"], os.path.pathsep.join(["test1", "test2"])),
        (clickqt.widgets.FilePathField, {"type":click.types.Path()}, "test", "test"),
        (clickqt.widgets.FilePathField, {"type":click.types.Path()}, ["test1", "test2"], os.path.pathsep.join(["test1", "test2"])),
        (clickqt.widgets.MultiValueWidget, {"type":click.types.Path(), "nargs":2}, ["a", "b"], ["a", "b"]),
        (clickqt.widgets.MultiValueWidget, {"type":click.types.File(), "nargs":2}, ["a", "b"], ["a", "b"]),
    ]
)
def test_set_envvar(clickqt_type:clickqt.widgets.BaseWidget, click_attrs:dict, envvar_values:str|list[str], expected:str|list[str]):
    os.environ["TEST_CLICKQT_ENVVAR"] = os.path.pathsep.join(envvar_values if isinstance(envvar_values, list) else [envvar_values])

    param = click.Option(param_decls=["--test"], envvar="TEST_CLICKQT_ENVVAR", **click_attrs)
    cli = click.Command("cli", params=[param])

    # Create type directly
    #widget: clickqt.widgets.BaseWidget = clickqt_type(otype=param.type, param=param, default=param.default, widgetsource=GUI().create_widget, com=cli)
    #assert widget.getWidgetValue() == expected, "directly"

    # clickqt creates the type
    control = clickqt.qtgui_from_click(cli)
    assert control.widget_registry[cli.name][param.name].getWidgetValue() == expected, "clickqt"

@pytest.mark.parametrize(
    ("clickqt_type", "click_attrs", "envvar_values", "expected"),
    [
        (clickqt.widgets.MultiValueWidget, {"type":click.types.Path(), "nargs":3}, ["a", "b"], "Takes 3 values but 2 were given."),
        (clickqt.widgets.MultiValueWidget, {"type":click.types.File(), "nargs":2}, ["a", "b", "c"], "Takes 2 values but 3 were given."),
        (clickqt.widgets.TupleWidget, {"type":(click.types.Path(), click.types.Path())}, ["a", "b", "c"], "Takes 2 values but 3 were given."),
        (clickqt.widgets.TupleWidget, {"type":(click.types.Path(), click.types.File())}, ["a"], "Takes 2 values but 1 was given."),
        (clickqt.widgets.TupleWidget, {"type":(click.types.File(), click.types.Path())}, ["a", "c", "b"], "Takes 2 values but 3 were given."),
        (clickqt.widgets.TupleWidget, {"type":(click.types.File(), click.types.File())}, ["a", "b", "c", "d"], "Takes 2 values but 4 were given."),
    ]
)
def test_set_envvar_fail(clickqt_type:clickqt.widgets.BaseWidget, click_attrs:dict, envvar_values:str|list[str], expected:str|list[str]):
    os.environ["TEST_CLICKQT_ENVVAR"] = os.path.pathsep.join(envvar_values if isinstance(envvar_values, list) else [envvar_values])

    param = click.Option(param_decls=["--test"], envvar="TEST_CLICKQT_ENVVAR", **click_attrs)
    cli = click.Command("cli", params=[param])

    # Create type directly
    #widget: clickqt.widgets.BaseWidget = clickqt_type(otype=param.type, param=param, default=param.default, widgetsource=GUI().create_widget, com=cli)
    #assert widget.getWidgetValue() == expected, "directly"

    # clickqt creates the type
    with pytest.raises(click.exceptions.BadParameter) as exc_info:
        clickqt.qtgui_from_click(cli).widget_registry[cli.name][param.name]

    assert expected in exc_info.value.message, "clickqt"
