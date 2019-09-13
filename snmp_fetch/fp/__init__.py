"""Functional programming structures."""

from functools import partial
from typing import Any, Callable, Sequence, TypeVar

from snmp_fetch.fp import either, maybe

__all__ = ['either', 'maybe']

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')

T = TypeVar('T')

F = partial


def curry2(f: Callable[[A, B], C]) -> Callable[[A], Callable[[B], C]]:
    """Curry a two argument function."""
    return lambda a: lambda b: f(a, b)


def star(
        f: Callable[..., T], *args: Any, **kwargs: Any
) -> Callable[[Sequence[Any]], T]:
    """Return a partial function that apply args with the star operator."""
    def apply(params: Sequence[Any]) -> T:
        return f(*params, *args, **kwargs)
    return apply
