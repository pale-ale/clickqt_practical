import typing as t
import pytest
import click
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QClipboard
import clickqt.widgets
from tests.testutils import ClickAttrs


@pytest.mark.parametrize(
    ("click_attrs", "value", "expected_output"),
    [
        (ClickAttrs.intfield(), 12, "main  --p 12"),
        (ClickAttrs.textfield(), "test", "main  --p test"),
        (ClickAttrs.realfield(), 0.8, "main  --p 0.8"),
        (ClickAttrs.passwordfield(), "abc", "main  --p abc"),
        (ClickAttrs.checkbox(), True, "main  --p True"),
        (ClickAttrs.checkbox(), False, "main  --p False"),
        (ClickAttrs.intrange(maxval=2, clamp=True), 5, "main  --p 2"),
        (ClickAttrs.floatrange(maxval=2.05, clamp=True), 5, "main  --p 2.05"),
        (
            ClickAttrs.combobox(
                choices=["A", "B", "C"], case_sensitive=False, confirmation_prompt=True
            ),
            "B",
            "main  --p=B",
        ),
        (
            ClickAttrs.combobox(choices=["A", "B", "C"], case_sensitive=False),
            "B",
            "main  --p=B",
        ),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["B", "C"],
            "main  --p=B --p=C",
        ),
        (ClickAttrs.checkable_combobox(choices=["A", "B", "C"]), ["A"], "main  --p=A"),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["A", "B", "C"],
            "main  --p=A --p=B --p=C",
        ),
        (
            ClickAttrs.tuple_widget(types=(str, int, float)),
            ("t", 1, -2.0),
            "main  --p  t  1  -2.0",
        ),
        (
            ClickAttrs.nvalue_widget(type=(str, int)),
            [["a", 12], ["b", 11]],
            "main  --p   a   12  --p   b   11 ",
        ),
        (
            (
                ClickAttrs.multi_value_widget(nargs=2),
                ["foo", "bar"],
                "main  --p  foo  bar",
            )
        ),
        (
            ClickAttrs.multi_value_widget(nargs=2, default=["A", "B"]),
            ["A", "C"],
            "main  --p  A  C",
        ),
        (
            ClickAttrs.multi_value_widget(nargs=2, default=["A", "B"]),
            [" ", " "],
            "main  --p      ",
        ),
        (
            ClickAttrs.nvalue_widget(type=(click.types.File(), int)),
            [[".gitignore", 12], ["setup.py", -1]],
            "main  --p   .gitignore   12  --p   setup.py   -1 ",
        ),
    ],
)
def test_command_with_ep(click_attrs: dict, value: t.Any, expected_output: str):
    param = click.Option(param_decls=["--p"], **click_attrs)
    cli = click.Command("cli", params=[param])
    control = clickqt.qtgui_from_click(cli)
    control.set_ep_or_path("main")
    control.set_is_ep(True)
    widget = control.widget_registry[cli.name][param.name]
    widget.set_value(value)

    control.construct_command_string()

    assert control.is_ep is True
    assert control.ep_or_path == "main"
    assert control.cmd == cli

    # Simulate clipboard behavior using QApplication.clipboard()
    clipboard = QApplication.clipboard()
    print(clipboard.text(QClipboard.Clipboard))
    assert clipboard.text(QClipboard.Clipboard) == expected_output
