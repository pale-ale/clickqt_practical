import typing as t
import pytest
import click
import clickqt.widgets
from tests.testutils import ClickAttrs


def prepare_execution(cmd: click.Command, cmd_group_name: click.Group):
    return cmd_group_name.name + ":" + cmd.name


@pytest.mark.parametrize(
    ("click_attrs", "value", "fake_value"),
    [
        (ClickAttrs.intfield(), 12, 4),
        (ClickAttrs.textfield(), "test", "main --p test"),
        (ClickAttrs.realfield(), 0.8, 1.3),
        (ClickAttrs.passwordfield(), "abc", "main --p abc"),
        (ClickAttrs.checkbox(), True, False),
        (ClickAttrs.checkbox(), False, True),
        (ClickAttrs.intrange(maxval=2, clamp=True), 1, 0),
        (ClickAttrs.floatrange(maxval=2.05, clamp=True), 1.3, 0),
        (
            ClickAttrs.combobox(
                choices=["A", "B", "C"], case_sensitive=False, confirmation_prompt=True
            ),
            "B",
            "A",
        ),
        (
            ClickAttrs.combobox(choices=["A", "B", "C"], case_sensitive=False),
            "B",
            "A",
        ),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["B", "C"],
            ["A"],
        ),
        (ClickAttrs.checkable_combobox(choices=["A", "B", "C"]), ["A"], ["B"]),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["A", "B", "C"],
            [],
        ),
        (
            ClickAttrs.tuple_widget(types=(str, int, float)),
            ["t", 1, -2.0],
            ["\n", 3, -1.2],
        ),
        (
            ClickAttrs.nvalue_widget(type=(str, int)),
            [("a", 12), ("b", 11)],
            [("ddd", 22)],
        ),
        (
            (
                ClickAttrs.multi_value_widget(nargs=2),
                ["foo", "t"],
                ["1", "-- ~ \0"],
            )
        ),
        (
            ClickAttrs.multi_value_widget(nargs=2, default=["A", "B"]),
            ["A", "C"],
            ["X", "X"],
        ),
    ],
)
def test_import_ep(click_attrs: dict, value: t.Any, fake_value: t.Any):
    param = click.Option(param_decls=["--p"], **click_attrs)
    cli = click.Command("main", params=[param])
    control = clickqt.qtgui_from_click(cli)
    control.set_ep_or_path("main")
    control.set_is_ep(True)
    widget = control.widget_registry[cli.name][param.name]
    widget.set_value(value)

    # copy cmd string to clipboard
    control.construct_command_string()

    assert control.is_ep is True
    assert control.ep_or_path == "main"
    assert control.cmd == cli

    widget.set_value(fake_value)
    val, _ = widget.get_value()
    if isinstance(val, tuple):
        val = list(val)
    assert val == fake_value

    # read the cmd from clipboard
    control.import_cmdline()
    val, _ = widget.get_value()
    if isinstance(val, tuple):
        val = list(val)
    assert val == value
