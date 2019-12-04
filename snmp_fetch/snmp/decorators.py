"""Variable bindings."""

from operator import methodcaller
from typing import Any, Callable, Mapping, Optional, Sequence, Text, Tuple, Type, Union, cast

import numpy as np

from snmp_fetch.fp.maybe import Maybe
from .object_type import ObjectType

DTYPE_FIELDS_T = (  # pylint: disable=invalid-name
    Mapping[str, Union[Tuple[np.dtype, int], Tuple[np.dtype, int, Any]]]
)
NULL_VAR_BIND_T = Tuple[Sequence[int], Tuple[int, int]]  # pylint: disable=invalid-name


def object_type(
        parent: Optional[Type[ObjectType]] = None, oid: Optional[Text] = None
) -> Callable[[type], Type[ObjectType]]:
    """Decorate a class as an object type."""
    def _object_type(cls: Type[ObjectType]) -> Type[ObjectType]:
        if not issubclass(cls, ObjectType):
            raise TypeError('Can only decorate types of ObjectType')
        cls._parent = Maybe.from_optional(parent)  # pylint: disable=protected-access
        cls._oid = Maybe.from_optional(oid)  # pylint: disable=protected-access
        cls._parent.fmap(methodcaller('_append_child', cls))  # pylint: disable=protected-access
        return cls
    return _object_type


def pipeline_hook(at: Text) -> Callable[[Any], Any]:
    """Decorate a function to be a hook in an ObjectType processing pipeline."""
    def _hook(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
        setattr(f, '__hook__', at)
        return cast(Callable[[Any], Any], staticmethod(f))
    return _hook
