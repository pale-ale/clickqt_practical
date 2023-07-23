from __future__ import annotations

import typing as t

import click
import pytest

from tests.testutils import ClickAttrs, raise_
import clickqt.widgets
from clickqt.core.error import ClickQtError


@pytest.mark.parametrize(
    ("click_attrs", "value", "expected"),
    [
        (
            ClickAttrs.checkbox(callback=lambda ctx, param, value: not value),
            True,
            False,
        ),
        (ClickAttrs.intfield(callback=lambda a, b, value: value - 1), 12, 11),
        (ClickAttrs.realfield(callback=lambda a, b, value: value + 1.5), 10.5, 12),
        (ClickAttrs.realfield(callback=lambda a, b, value: None), -312.2, None),
        (
            ClickAttrs.realfield(callback=lambda a, b, value: "test"),
            14.2,
            "test",
        ),  # Return type can be completely different
        (
            ClickAttrs.datetime(callback=lambda a, b, value: "2023-06-23 15:14:20"),
            "2020-01-21 10:11:12",
            "2023-06-23 15:14:20",
        ),
        (
            ClickAttrs.nvalue_widget(type=float, callback=lambda a, b, value: 1),
            [14.2, -2.3],
            1,
        ),
        (
            ClickAttrs.tuple_widget(
                types=(int, str), callback=lambda a, b, value: [value[0] + 5, "test"]
            ),
            [10, "10"],
            [15, "test"],
        ),
        (
            ClickAttrs.multi_value_widget(
                nargs=2,
                type=int,
                callback=lambda a, b, value: [value[0] + 5, value[1] - 5],
            ),
            [10, 10],
            [15, 5],
        ),
        (
            ClickAttrs.nvalue_widget(
                type=(int, (str, float)),
                callback=lambda a, b, value: [
                    [value[0][0] + 4, [value[0][1][0] + "est", value[0][1][1] + 3]]
                ],
            ),
            [[1, ["t", 2.1]]],
            [[5, ["test", 5.1]]],
        ),
    ],
)
def test_callback(click_attrs: dict, value: t.Any, expected: t.Any):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])

    control = clickqt.qtgui_from_click(cli)
    control.widget_registry[cli.name][param.name].set_value(value)
    val, err = control.widget_registry[cli.name][param.name].get_value()

    assert val == expected and err.type == ClickQtError.ErrorType.NO_ERROR


@pytest.mark.parametrize(
    ("click_attrs", "value", "expected"),
    [
        (
            ClickAttrs.checkbox(
                callback=lambda ctx, param, value: raise_(Exception("..."))
            ),
            False,
            None,
        ),
        (
            ClickAttrs.intfield(
                callback=lambda a, b, c: raise_(click.BadParameter("..."))
            ),
            123,
            None,
        ),
        (
            ClickAttrs.nvalue_widget(
                type=(int, (str, float)),
                callback=lambda a, b, c: raise_(click.BadParameter("...")),
            ),
            [[1, ["t", 2.1]]],
            None,
        ),
    ],
)
def test_callback_fail(click_attrs: dict, value: t.Any, expected: t.Any):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])

    control = clickqt.qtgui_from_click(cli)
    control.widget_registry[cli.name][param.name].set_value(value)
    val, err = control.widget_registry[cli.name][param.name].get_value()

    assert val == expected and err.type == ClickQtError.ErrorType.PROCESSING_VALUE_ERROR


@pytest.mark.parametrize(
    ("click_attrs", "value", "expected"),
    [
        (ClickAttrs.intfield(callback=lambda ctx, param, value: ctx.abort()), 1, None),
        (
            ClickAttrs.nvalue_widget(
                type=(int, str), callback=lambda ctx, param, value: ctx.abort()
            ),
            [[1, "t"]],
            None,
        ),
    ],
)
def test_callback_abort(click_attrs: dict, value: t.Any, expected: t.Any):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])

    control = clickqt.qtgui_from_click(cli)
    control.widget_registry[cli.name][param.name].set_value(value)
    val, err = control.widget_registry[cli.name][param.name].get_value()

    assert val == expected and err.type == ClickQtError.ErrorType.ABORTED_ERROR


@pytest.mark.parametrize(
    ("click_attrs", "value", "expected"),
    [
        (
            ClickAttrs.textfield(callback=lambda ctx, param, value: ctx.exit()),
            "test",
            None,
        ),
        (
            ClickAttrs.nvalue_widget(
                type=(int, str), callback=lambda ctx, param, value: ctx.exit()
            ),
            [[1, "t"]],
            None,
        ),
    ],
)
def test_callback_exit(click_attrs: dict, value: t.Any, expected: t.Any):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])

    control = clickqt.qtgui_from_click(cli)
    control.widget_registry[cli.name][param.name].set_value(value)
    val, err = control.widget_registry[cli.name][param.name].get_value()

    assert val == expected and err.type == ClickQtError.ErrorType.EXIT_ERROR
