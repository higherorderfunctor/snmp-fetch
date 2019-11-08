"""Utility functions."""

import re
from functools import reduce
from typing import Any, Callable, Mapping, Sequence, Text, Tuple, TypeVar, Union, cast, overload

import numpy as np

from .fp.either import Either, Left, Right
from .fp.maybe import Just, Maybe, Nothing

FuncType = Callable[..., Any]
F = TypeVar('F', bound=FuncType)

DTYPE_FIELDS_T = (  # pylint: disable=invalid-name
    Mapping[str, Union[Tuple[np.dtype, int], Tuple[np.dtype, int, Any]]]
)


def monkeypatch(cls: type, method: Text) -> Callable[[F], F]:
    """Monkey patch and store base method on the function object."""
    def patch(f: F) -> F:
        if not getattr(cls, method) == f:
            setattr(f, method, getattr(cls, method))
            setattr(cls, method, f)
        return f
    return patch


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


def dtype_fields(d: np.dtype) -> Either[Exception, DTYPE_FIELDS_T]:
    """Get structured dtype fields safely."""
    if d.fields is None:
        return Left(ValueError(f'structured dtype required: {d}'))
    return Right(d.fields)


def concat_dtypes(ds: Sequence[np.dtype]) -> np.dtype:
    """Concat structured datatypes."""
    def _concat(
            acc: Tuple[Mapping[Any, Any], int], a: np.dtype
    ) -> Tuple[DTYPE_FIELDS_T, int]:
        acc_fields, acc_itemsize = acc
        fields = dtype_fields(a).throw()
        intersection = set(acc_fields).intersection(set(fields))
        if intersection != set():
            raise ValueError(f'dtypes have overlapping fields: {intersection}')
        return (
            {
                **acc_fields,
                **{k: (d[0], d[1] + acc_itemsize) for k, d in fields.items()}
            },
            acc_itemsize + a.itemsize
        )
    # dtype.fields() doesn't match dtype constructor despite being compatible
    return np.dtype(reduce(_concat, ds, (cast(DTYPE_FIELDS_T, {}), 0))[0])  # type: ignore


def concatv_dtypes(*args: np.dtype) -> np.dtype:
    """Concat structured datatypes."""
    return concat_dtypes(args)


def dtype_array(d: Union[np.dtype, type], size: int) -> Maybe[np.dtype]:
    """Return an (n,) datatype if possible.

    Returns a bare datatype for a scalar request or Nothing with a negative size.
    """
    if size <= 0:
        return Nothing()
    if size == 1:
        if isinstance(d, np.dtype):
            return Just(d)
        return Just(np.dtype(d))
    return Just(np.dtype((d, size)))


def cuint8_to_int(x: np.ndarray) -> int:
    """Cast array elements to uint8 and converter to a single integer."""
    return int.from_bytes(x.astype(np.uint8).tobytes(), byteorder='big')
