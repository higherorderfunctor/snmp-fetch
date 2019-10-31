"""Utility functions."""

from typing import Any, Callable, Text, TypeVar

FuncType = Callable[..., Any]
F = TypeVar('F', bound=FuncType)


def monkeypatch(cls: type, method: Text) -> Callable[[F], F]:
    """Monkey patch and store base method on the function object."""
    def patch(f: F) -> F:
        if not getattr(cls, method) == f:
            setattr(f, method, getattr(cls, method))
            setattr(cls, method, f)
        return f
    return patch
