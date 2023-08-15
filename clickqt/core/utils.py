from __future__ import annotations
from click import Parameter


def remove_prefix(text: str, prefix: str):
    if text.startswith(prefix):
        return text[len(prefix) :]

    return text


def is_param_arg(parameter: Parameter):
    return not any(o.startswith("-") for o in parameter.opts)
