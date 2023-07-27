import typing as t
import pytest
import click
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QClipboard
import clickqt.widgets
from tests.testutils import ClickAttrs


@pytest.mark.parametrize(
    ("click_attrs", "value", "expected_output"),
    [(ClickAttrs.intfield(), 12, "main  --p 12")],
)
def test_command_with_ep(click_attrs: dict, value: t.Any, expected_output: str):
    param = click.Option(param_decls=["--p"], **click_attrs)
    cli = click.Command("cli", params=[param])
    control = clickqt.qtgui_from_click(cli)
    control.set_ep_or_path("main")
    control.set_is_ep(True)
    widget = control.widget_registry[cli.name][param.name]
    widget.setValue(value)

    control.construct_command_string()

    assert control.is_ep is True
    assert control.ep_or_path == "main"
    assert control.cmd == cli

    # Simulate clipboard behavior using QApplication.clipboard()
    clipboard = QApplication.clipboard()
    assert clipboard.text(QClipboard.Clipboard) == expected_output
