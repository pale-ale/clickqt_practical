from __future__ import annotations

import typing as t

import click
import pytest

from tests.testutils import ClickAttrs
import clickqt.widgets


@pytest.mark.parametrize(
    ("click_attrs_list", "group_name", "cli_names_list", "expected"),
    [
        (
            [
                [ClickAttrs.checkbox(), ClickAttrs.intfield()],
                [ClickAttrs.realfield(), ClickAttrs.passwordfield()],
            ],
            "test_group",
            ["cli1", "cli2"],
            ["test_group:cli1", "test_group:cli2"],
        ),
        (
            [
                [ClickAttrs.filefield(), ClickAttrs.filepathfield()],
                [ClickAttrs.tuple_widget(types=(click.types.Path(), int))],
            ],
            "abc",
            ["abc", "abc23"],
            ["abc:abc", "abc:abc23"],
        ),
    ],
)
def test_widget_registry_command_names(
    click_attrs_list: t.Iterable[t.Iterable[dict]],
    group_name: str,
    cli_names_list: t.Iterable[str],
    expected: t.Iterable[str],
):
    clis = []

    for i, cli_params in enumerate(click_attrs_list):
        params = []

        for j, click_attrs in enumerate(cli_params):
            params.append(click.Option(param_decls=["--test" + str(j)], **click_attrs))

        clis.append(click.Command(cli_names_list[i], params=params))

    group = click.Group(group_name, commands=clis)

    control = clickqt.qtgui_from_click(group)
    assert len(control.widget_registry) == len(cli_names_list)
    for i, cli_name in enumerate(control.widget_registry.keys()):
        assert cli_name == expected[i]
