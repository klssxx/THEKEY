"""THEKEY Core - canonical demo app.

NOTE: This ORIGINAL file is intentionally defective: ``add`` implements
subtraction. It MUST remain broken after every run. Only the isolated workspace
copy is repaired by a governed run. Do not "fix" this file.
"""


def add(a: int, b: int) -> int:
    return a - b


def subtract(a: int, b: int) -> int:
    return a - b
