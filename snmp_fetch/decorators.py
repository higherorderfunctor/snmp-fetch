"""Variable bindings."""

from typing import Any, Callable, Mapping, Optional, Sequence, Text, Tuple, Type, Union, cast

import numpy as np

from .fp.maybe import Maybe
from .object_type import ObjectType

DTYPE_FIELDS_T = (  # pylint: disable=invalid-name
    Mapping[str, Union[Tuple[np.dtype, int], Tuple[np.dtype, int, Any]]]
)
NULL_VAR_BIND_T = Tuple[Sequence[int], Tuple[int, int]]  # pylint: disable=invalid-name


def object_type(
        parent: Optional[Type[ObjectType]] = None, oid: Optional[Text] = None
) -> Callable[[type], Type[ObjectType]]:
    """Decorate a class as an object type."""
    def _object_type(cls: type) -> Type[ObjectType]:
        return type(
            cls.__name__, (cls, ObjectType), {
                '__module__': cls.__module__,
                '__slots__': [],
                '__doc__': cls.__doc__,
                '_parent': Maybe.from_optional(parent),
                '_oid': Maybe.from_optional(oid)
            }
        )
    return _object_type


def pipeline_hook(at: Text) -> Callable[[Any], Any]:
    """Decorate a function to be a hook in an ObjectType processing pipeline."""
    def _hook(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
        setattr(f, '__hook__', at)
        return cast(Callable[[Any], Any], staticmethod(f))
    return _hook
