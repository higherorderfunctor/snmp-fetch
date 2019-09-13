"""Utility functions."""

import re
from typing import Sequence, Text, Union, overload


def align64(x: int) -> int:
    """Align a size to be a multiple of 64."""
    if x < 0 or x >= 2 ** 64:
        raise ValueError(
            'integer does not fall between (' + str((2 ** 64) - 1) + ')'
        )
    return (x + 7) & ~0x07


@overload
def convert_oid(oid: Text) -> Sequence[int]:
    # pylint: disable=unused-argument
    # pragma: no cover
    """Convert a text oid to a sequence of integers."""
    ...  # pragma: no cover


@overload
def convert_oid(oid: Sequence[int]) -> Text:
    # pylint: disable=function-redefined, unused-argument
    # pragma: no cover
    """Convert a sequence of integers to a text oid."""
    ...  # pragma: no cover


def convert_oid(
        oid: Union[Text, Sequence[int]]
) -> Union[Sequence[int], Text]:
    # pylint: disable=function-redefined
    """Convert an oid between text and sequence of integers."""
    if isinstance(oid, Text):
        if re.match(r'^\.?\d+(\.\d+)*$', oid):
            if oid.startswith('.'):
                oid = oid[1:]
            return [int(x) for x in (oid).split('.')]
        raise ValueError(f'{oid} is not a valid oid')
    return '.'+'.'.join(map(str, oid))


@overload
def validate_oid(oid: Text) -> Text:
    # pylint: disable=unused-argument
    # pragma: no cover
    """Validate a text oid."""
    ...  # pragma: no cover


@overload
def validate_oid(oid: Sequence[int]) -> Sequence[int]:
    # pylint: disable=function-redefined, unused-argument
    """Validate a sequence of integers oid."""
    ...  # pragma: no cover


def validate_oid(
        oid: Union[Text, Sequence[int]]
) -> Union[Text, Sequence[int]]:
    """Validate an oid."""
    # pylint: disable=function-redefined
    return convert_oid(convert_oid(oid))
