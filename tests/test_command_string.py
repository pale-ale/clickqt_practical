import typing as t
import pytest
import click
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QClipboard
import clickqt.widgets
from tests.testutils import ClickAttrs


def prepare_execution(cmd: click.Command, cmd_group_name: click.Group):
    return cmd_group_name.name + ":" + cmd.name


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


@pytest.mark.parametrize(
    ("click_attrs", "value", "expected_output"),
    [
        (ClickAttrs.intfield(), 12, "python example/example/main.py  --p 12"),
        (ClickAttrs.textfield(), "test", "python example/example/main.py  --p test"),
        (ClickAttrs.realfield(), 0.8, "python example/example/main.py  --p 0.8"),
        (ClickAttrs.passwordfield(), "abc", "python example/example/main.py  --p abc"),
        (ClickAttrs.checkbox(), True, "python example/example/main.py  --p True"),
        (ClickAttrs.checkbox(), False, "python example/example/main.py  --p False"),
        (
            ClickAttrs.intrange(maxval=2, clamp=True),
            5,
            "python example/example/main.py  --p 2",
        ),
        (
            ClickAttrs.floatrange(maxval=2.05, clamp=True),
            5,
            "python example/example/main.py  --p 2.05",
        ),
        (
            ClickAttrs.combobox(
                choices=["A", "B", "C"], case_sensitive=False, confirmation_prompt=True
            ),
            "B",
            "python example/example/main.py  --p=B",
        ),
        (
            ClickAttrs.combobox(choices=["A", "B", "C"], case_sensitive=False),
            "B",
            "python example/example/main.py  --p=B",
        ),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["B", "C"],
            "python example/example/main.py  --p=B --p=C",
        ),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["A"],
            "python example/example/main.py  --p=A",
        ),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["A", "B", "C"],
            "python example/example/main.py  --p=A --p=B --p=C",
        ),
        (
            ClickAttrs.tuple_widget(types=(str, int, float)),
            ("t", 1, -2.0),
            "python example/example/main.py  --p  t  1  -2.0",
        ),
        (
            ClickAttrs.nvalue_widget(type=(str, int)),
            [["a", 12], ["b", 11]],
            "python example/example/main.py  --p   a   12  --p   b   11 ",
        ),
        (
            (
                ClickAttrs.multi_value_widget(nargs=2),
                ["foo", "bar"],
                "python example/example/main.py  --p  foo  bar",
            )
        ),
        (
            ClickAttrs.multi_value_widget(nargs=2, default=["A", "B"]),
            ["A", "C"],
            "python example/example/main.py  --p  A  C",
        ),
        (
            ClickAttrs.multi_value_widget(nargs=2, default=["A", "B"]),
            [" ", " "],
            "python example/example/main.py  --p      ",
        ),
        (
            ClickAttrs.nvalue_widget(type=(click.types.File(), int)),
            [[".gitignore", 12], ["setup.py", -1]],
            "python example/example/main.py  --p   .gitignore   12  --p   setup.py   -1 ",
        ),
    ],
)
def test_construct_cmd_string_file(
    click_attrs: dict, value: t.Any, expected_output: str
):
    param = click.Option(param_decls=["--p"], **click_attrs)
    cli = click.Command("cli", params=[param])
    control = clickqt.qtgui_from_click(cli)
    control.set_ep_or_path("example/example/main.py")
    control.set_is_ep(False)
    widget = control.widget_registry[cli.name][param.name]
    widget.set_value(value)

    control.construct_command_string()

    assert control.is_ep is False
    assert control.ep_or_path == "example/example/main.py"
    assert control.cmd == cli

    # Simulate clipboard behavior using QApplication.clipboard()
    clipboard = QApplication.clipboard()
    print(clipboard.text(QClipboard.Clipboard))
    assert clipboard.text(QClipboard.Clipboard) == expected_output


@pytest.mark.parametrize(
    ("click_attrs", "value", "expected_output"),
    [
        (ClickAttrs.intfield(), 12, "main  cmd --p 12"),
        (ClickAttrs.textfield(), "test", "main  cmd --p test"),
        (ClickAttrs.realfield(), 0.8, "main  cmd --p 0.8"),
        (ClickAttrs.passwordfield(), "abc", "main  cmd --p abc"),
        (ClickAttrs.checkbox(), True, "main  cmd --p True"),
        (ClickAttrs.checkbox(), False, "main  cmd --p False"),
        (ClickAttrs.intrange(maxval=2, clamp=True), 5, "main  cmd --p 2"),
        (ClickAttrs.floatrange(maxval=2.05, clamp=True), 5, "main  cmd --p 2.05"),
        (
            ClickAttrs.combobox(
                choices=["A", "B", "C"], case_sensitive=False, confirmation_prompt=True
            ),
            "B",
            "main  cmd --p=B",
        ),
        (
            ClickAttrs.combobox(choices=["A", "B", "C"], case_sensitive=False),
            "B",
            "main  cmd --p=B",
        ),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["B", "C"],
            "main  cmd --p=B --p=C",
        ),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["A"],
            "main  cmd --p=A",
        ),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["A", "B", "C"],
            "main  cmd --p=A --p=B --p=C",
        ),
        (
            ClickAttrs.tuple_widget(types=(str, int, float)),
            ("t", 1, -2.0),
            "main  cmd --p  t  1  -2.0",
        ),
        (
            ClickAttrs.nvalue_widget(type=(str, int)),
            [["a", 12], ["b", 11]],
            "main  cmd --p   a   12  --p   b   11 ",
        ),
        (
            (
                ClickAttrs.multi_value_widget(nargs=2),
                ["foo", "bar"],
                "main  cmd --p  foo  bar",
            )
        ),
        (
            ClickAttrs.multi_value_widget(nargs=2, default=["A", "B"]),
            ["A", "C"],
            "main  cmd --p  A  C",
        ),
        (
            ClickAttrs.multi_value_widget(nargs=2, default=["A", "B"]),
            [" ", " "],
            "main  cmd --p      ",
        ),
        (
            ClickAttrs.nvalue_widget(type=(click.types.File(), int)),
            [[".gitignore", 12], ["setup.py", -1]],
            "main  cmd --p   .gitignore   12  --p   setup.py   -1 ",
        ),
    ],
)
def test_command_with_ep_group(click_attrs: dict, value: t.Any, expected_output: str):
    param = click.Option(param_decls=["--p"], **click_attrs)
    cli = click.Group("cli")
    cmd = click.Command("cmd", params=[param])
    cli.add_command(cmd)
    control = clickqt.qtgui_from_click(cli)
    control.set_ep_or_path("main")
    control.set_is_ep(True)
    widget = control.widget_registry[prepare_execution(cmd, cli)][param.name]
    widget.set_value(value)

    control.construct_command_string()

    assert control.is_ep is True
    assert control.ep_or_path == "main"
    assert control.cmd == cli

    # Simulate clipboard behavior using QApplication.clipboard()
    clipboard = QApplication.clipboard()
    print(clipboard.text(QClipboard.Clipboard))
    assert clipboard.text(QClipboard.Clipboard) == expected_output


@pytest.mark.parametrize(
    ("click_attrs", "value", "expected_output"),
    [
        (ClickAttrs.intfield(), 12, "python example/example/main.py  cmd --p 12"),
        (
            ClickAttrs.textfield(),
            "test",
            "python example/example/main.py  cmd --p test",
        ),
        (ClickAttrs.realfield(), 0.8, "python example/example/main.py  cmd --p 0.8"),
        (
            ClickAttrs.passwordfield(),
            "abc",
            "python example/example/main.py  cmd --p abc",
        ),
        (ClickAttrs.checkbox(), True, "python example/example/main.py  cmd --p True"),
        (ClickAttrs.checkbox(), False, "python example/example/main.py  cmd --p False"),
        (
            ClickAttrs.intrange(maxval=2, clamp=True),
            5,
            "python example/example/main.py  cmd --p 2",
        ),
        (
            ClickAttrs.floatrange(maxval=2.05, clamp=True),
            5,
            "python example/example/main.py  cmd --p 2.05",
        ),
        (
            ClickAttrs.combobox(
                choices=["A", "B", "C"], case_sensitive=False, confirmation_prompt=True
            ),
            "B",
            "python example/example/main.py  cmd --p=B",
        ),
        (
            ClickAttrs.combobox(choices=["A", "B", "C"], case_sensitive=False),
            "B",
            "python example/example/main.py  cmd --p=B",
        ),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["B", "C"],
            "python example/example/main.py  cmd --p=B --p=C",
        ),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["A"],
            "python example/example/main.py  cmd --p=A",
        ),
        (
            ClickAttrs.checkable_combobox(choices=["A", "B", "C"]),
            ["A", "B", "C"],
            "python example/example/main.py  cmd --p=A --p=B --p=C",
        ),
        (
            ClickAttrs.tuple_widget(types=(str, int, float)),
            ("t", 1, -2.0),
            "python example/example/main.py  cmd --p  t  1  -2.0",
        ),
        (
            ClickAttrs.nvalue_widget(type=(str, int)),
            [["a", 12], ["b", 11]],
            "python example/example/main.py  cmd --p   a   12  --p   b   11 ",
        ),
        (
            (
                ClickAttrs.multi_value_widget(nargs=2),
                ["foo", "bar"],
                "python example/example/main.py  cmd --p  foo  bar",
            )
        ),
        (
            ClickAttrs.multi_value_widget(nargs=2, default=["A", "B"]),
            ["A", "C"],
            "python example/example/main.py  cmd --p  A  C",
        ),
        (
            ClickAttrs.multi_value_widget(nargs=2, default=["A", "B"]),
            [" ", " "],
            "python example/example/main.py  cmd --p      ",
        ),
        (
            ClickAttrs.nvalue_widget(type=(click.types.File(), int)),
            [[".gitignore", 12], ["setup.py", -1]],
            "python example/example/main.py  cmd --p   .gitignore   12  --p   setup.py   -1 ",
        ),
    ],
)
def test_construct_cmd_string_file_grouped(
    click_attrs: dict, value: t.Any, expected_output: str
):
    param = click.Option(param_decls=["--p"], **click_attrs)
    cli = click.Group("cli")
    cmd = click.Command("cmd", params=[param])
    cli.add_command(cmd)
    control = clickqt.qtgui_from_click(cli)
    control.set_ep_or_path("example/example/main.py")
    control.set_is_ep(False)
    widget = control.widget_registry[prepare_execution(cmd, cli)][param.name]
    widget.set_value(value)

    control.construct_command_string()

    assert control.is_ep is False
    assert control.ep_or_path == "example/example/main.py"
    assert control.cmd == cli

    # Simulate clipboard behavior using QApplication.clipboard()
    clipboard = QApplication.clipboard()
    print(clipboard.text(QClipboard.Clipboard))
    assert clipboard.text(QClipboard.Clipboard) == expected_output
