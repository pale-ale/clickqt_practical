import click
import pytest
from clickqt import qtgui_from_click
from clickqt.core.control import Control
from tests.testutils import ClickAttrs


def ensure_cmdstr(control: Control, template: str):
    control.construct_command_string()
    cmdstr = control.get_clipboard()
    assert cmdstr == template


@pytest.mark.parametrize(
    ["attrs", "value", "template"],
    [
        (ClickAttrs.checkbox(), "True", "--opt True"),
        (ClickAttrs.checkbox(is_flag=True), "True", "--opt"),
        (
            ClickAttrs.checkable_combobox(["A1", "B2", "C3"]),
            ["B2", "C3"],
            "--opt B2 --opt C3",
        ),
        (ClickAttrs.filefield(), "/home", "--opt /home"),
        (ClickAttrs.datetime(), "2001-1-1", "--opt '2001-01-01 00:00:00'"),
        (ClickAttrs.floatrange(minval=-10), "-2.03", "--opt -2.03"),
        (ClickAttrs.countwidget(), 3, "--opt --opt --opt"),
        (
            ClickAttrs.nvalue_widget(type=(str, int)),
            [["a", 12], ["b", 11]],
            "--opt a 12 --opt b 11",
        ),
        (
            ClickAttrs.tuple_widget(types=(str, int, float)),
            ("t", 1, -2.0),
            "--opt t 1 -2.0",
        ),
        (
            ClickAttrs.multi_value_widget(nargs=2),
            ["A", "C"],
            "--opt A C",
        ),
    ],
)
def test_disable(attrs, value, template):
    standard_opt = click.Option(["--standard"], default="te st")
    opt = click.Option(["--opt"], **attrs, default=value)
    cmd = click.Command("cmd", params=[standard_opt, opt])
    control = qtgui_from_click(cmd)
    widget = control.widget_registry[cmd.name][opt.name]

    expected_enabled = "--standard 'te st' " + template
    expected_disabled = "--standard 'te st'"

    ensure_cmdstr(control, expected_enabled)
    widget.set_enabled_changeable(enabled=False)
    ensure_cmdstr(control, expected_disabled)
    widget.set_enabled_changeable(enabled=True)
    ensure_cmdstr(control, expected_enabled)
