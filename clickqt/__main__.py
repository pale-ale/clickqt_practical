"""
Contains the entry point for clickqt, called clickqtfy, allowing external use.
"""
from __future__ import annotations

import sys
from importlib import util, metadata

import click
from clickqt.core.core import qtgui_from_click


@click.command("clickqtfy")
@click.argument("entrypoint")
@click.argument("funcname", default=None, required=False)
def clickqtfy(entrypoint, funcname):
    """
    Generate a GUI for an entry point or a file + click.command combinaiton.

    ENTRYPOINT: Name of an installed entry point or a file path.\n
    FUNCNAME: Name of the click.command inside the file at ENTRYPOINT.\n
    If FUNCNAME is provided, ENTRYPOINT is interpreted as a file. Otherwise, as an entry point.
    """
    if funcname:
        fileparam = click.types.File()
        fileparam.convert(entrypoint, None, None)
        control = qtgui_from_click(get_command_from_path(entrypoint, funcname))
        control.set_ep_or_path(entrypoint)
        control.set_is_ep(False)
    else:
        control = qtgui_from_click(get_command_from_entrypoint(entrypoint))
        control.set_ep_or_path(entrypoint)
        control.set_is_ep(True)
    
    return control()


def get_command_from_entrypoint(epname: str) -> click.Command:
    """
    Returns the click.Command specified by `epname`.
    If `epname` is not a click.Command, raises `ImportError`.
    """
    eps = get_entrypoints_from_name(epname)
    if len(eps) == 0:
        raise ImportError(f"No entry point named '{epname}' found.")
    if len(eps) > 1:
        concateps = "\n".join([ep.name for ep in eps])
        raise ImportError(
            f"No entry point named '{epname}' found. Similar ones:\n{concateps}"
        )
    return validate_entrypoint(eps[0].load())


def get_entrypoints_from_name(epname: str) -> list[metadata.EntryPoint]:
    """
    Returns the entrypoints that include `epname` in their name.
    """
    grouped_eps = metadata.entry_points()
    candidates: list[metadata.EntryPoint] = []
    for group in grouped_eps.values():
        for entrypoint in group:
            if entrypoint.name == epname:
                return [entrypoint]
            if epname in entrypoint.name or epname in entrypoint.value:
                candidates.append(entrypoint)
    return candidates


def get_command_from_path(eppath: str, epname: str) -> click.Command:
    """
    Returns the entrypoint given by the file path and the function name,
    or raises `ImportError` if the endpoint is not a `click.Command`.
    """
    modulename = "clickqtfy.imported_module"
    spec = util.spec_from_file_location(modulename, eppath)
    module = util.module_from_spec(spec)
    sys.modules[modulename] = module
    spec.loader.exec_module(module)
    entrypoint = getattr(module, epname, None)
    if entrypoint is None:
        raise ImportError(
            f"Module '{spec.origin}' does not contain the entry point '{epname}'."
        )
    return validate_entrypoint(entrypoint)


def validate_entrypoint(entrypoint):
    """
    Raise a `TypeError` if a provided function is not a `click.Command`.
    """
    if not isinstance(entrypoint, click.Command):
        raise TypeError(f"Entry point '{entrypoint}' is not a 'click.Command'.")
    return entrypoint
