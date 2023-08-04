"""
Tests the external use of clickqt.
"""
from __future__ import annotations

import pytest
import click
from clickqt.__main__ import (
    get_command_from_entrypoint,
    get_command_from_path,
    get_gui_specs_from_entrypoint,
    get_gui_specs_from_path,
)


def test_clickqt_external():
    """
    Try some good/bad imports and check if they are recognized as commands/garbage.
    """
    # test with endpoint
    with pytest.raises(ImportError):
        get_command_from_entrypoint("example")
    with pytest.raises(TypeError):
        get_command_from_entrypoint("example_gui")
    assert isinstance(get_command_from_entrypoint("example_cli"), click.Command)

    # test with file
    with pytest.raises(ImportError):
        get_command_from_path("example/example/afwizard.py", "ma")
    with pytest.raises(FileNotFoundError):
        get_command_from_path("example/example/--_--_-_.py", "main")
    with pytest.raises(TypeError):
        get_command_from_path(
            "example/example/afwizard.py", "validate_spatial_reference"
        )
    assert isinstance(
        get_command_from_path("example/example/afwizard.py", "main"), click.Command
    )


def test_clickqt_external_gui_specs():
    # test with gui endpoint
    with pytest.raises(ImportError):
        get_gui_specs_from_entrypoint("main")
    with pytest.raises(TypeError):
        get_gui_specs_from_entrypoint("example_cli")
    assert isinstance(get_gui_specs_from_entrypoint("example_gui"), dict)

    # test with file
    with pytest.raises(ImportError):
        get_gui_specs_from_path("example/example/afwizard.py", "example_cli")
    with pytest.raises(TypeError):
        get_gui_specs_from_path(
            "example/example/afwizard.py", "validate_spatial_reference"
        )
    with pytest.raises(FileNotFoundError):
        get_gui_specs_from_path("example/example/-.py", "gui")
    assert isinstance(
        get_gui_specs_from_path("example/example/__main__.py", "gui"), dict
    )
