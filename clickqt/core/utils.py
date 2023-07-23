from __future__ import annotations

import re


def is_nested_list(lst):
    if isinstance(lst, list):
        return any(isinstance(item, list) for item in lst)
    return False


def is_file_path(string):
    # Regular expression pattern to match file paths
    pattern = r"^([a-zA-Z]:)?[\\/](?:[^\0<>:\/\\|?*\n]+[\\/])*[^\0<>:\/\\|?*\n]*$"

    # Check if the string matches the pattern
    return re.match(pattern, string)


def remove_prefix(text: str, prefix: str):
    if text.startswith(prefix):
        return text[len(prefix) :]

    return text
