"""Pylint hints for the C++ API extension."""

from typing import Any

import astroid
from astroid import MANAGER


def register(_: Any) -> None:
    # pylint: disable=unnecessary-pass
    """Register the plugin."""
    pass


def transform(cls: Any) -> None:
    """Apply the node transformations."""
    if cls.name == 'NullVarBind':
        cls.locals['oid'] = [astroid.List(parent=cls)]
    elif cls.name == 'ObjectIdentityParameter':
        cls.locals['start'] = [astroid.List(parent=cls)]
        cls.locals['end'] = [astroid.List(parent=cls)]


MANAGER.register_transform(astroid.ClassDef, transform)
