"""Pandas extension utilities."""

from typing import Iterator, Optional, Sequence, Text


def column_names(
        n: Optional[int] = None, alphabet: Sequence[Text] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
) -> Iterator[Text]:
    """Generate unique temporary column names."""
    base_gen = column_names(alphabet=alphabet)
    base = ''
    letters = alphabet
    while True:
        if n is not None:
            if n <= 0:
                return
            n = n - 1
        if not letters:
            base = next(base_gen)  # pylint: disable=stop-iteration-return  # infinite generator
            letters = alphabet
        column, letters = letters[0], letters[1:]
        yield base + column
