"""Variable bindings."""

import re
from functools import reduce
from operator import add
from typing import Any, Callable, Mapping, Optional, Sequence, Text, Tuple, Union, cast, overload

import attr
import numpy as np
from toolz.functoolz import compose, identity

from .fp import curry2
from .fp.either import Either, Left, Right
from .fp.maybe import Just, Maybe, Nothing

DTYPE_FIELDS_T = (  # pylint: disable=invalid-name
    Mapping[str, Union[Tuple[np.dtype, int], Tuple[np.dtype, int, Any]]]
)


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


def get_fields(d: np.dtype) -> Either[Exception, DTYPE_FIELDS_T]:
    """Get structured dtype fields safely."""
    if d.fields is None:
        return Left(ValueError(f'structured dtype required: {d}'))
    return Right(d.fields)


def dtype_concat(ds: Sequence[np.dtype]) -> np.dtype:
    """Concat structured datatypes."""
    def _concat(
            acc: Tuple[Mapping[Any, Any], int], a: np.dtype
    ) -> Tuple[DTYPE_FIELDS_T, int]:
        acc_fields, acc_itemsize = acc
        fields = get_fields(a).throw()
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


def dtype_array(d: np.dtype, size: int) -> Maybe[np.dtype]:
    """Return an (n,) datatype if possible.

    Returns a bare datatype for a scalar request or Nothing with a negative size.
    """
    if size <= 0:
        return Nothing()
    if size == 1:
        return Just(d)
    return Just(np.dtype((d, size)))


def maybe_oid(value: Optional[Text]) -> Maybe[Text]:
    """Convert and validate Optional[Text] representation of OID to Maybe[Text]."""
    return Maybe.from_optional(value).fmap(validate_oid)


def maybe_dtype(value: Optional[np.dtype]) -> Maybe[np.dtype]:
    """Convert and validate Optional[dtype] to Maybe[dtype]."""
    if value is not None:
        if value.fields is None:
            raise ValueError(f'structured dtype required: {value}')
        if value.itemsize % 8 != 0:
            raise ValueError(f'dtype required to be 8 bytes aligned: {value}')
    return Maybe.from_optional(value)


@attr.s(frozen=True, slots=True)
class VarBind:
    """Variable binding."""

    oid: Maybe[Text] = attr.ib(
        default=None, converter=maybe_oid
    )
    index: Maybe[np.dtype] = attr.ib(
        default=None, converter=maybe_dtype
    )
    data: Maybe[np.dtype] = attr.ib(
        default=None, converter=maybe_dtype
    )
    op: Callable[[Any], Any] = attr.ib(
        default=identity
    )

    def __lshift__(self, other: 'VarBind') -> 'VarBind':
        # pylint: disable=no-member
        """Combine variable bindings."""
        return VarBind(
            oid=(
                self.oid
                .combine(curry2(add), other.oid)
                .to_optional()
            ),
            index=(
                self.index
                .combine(
                    lambda x: lambda y: dtype_concat([x, y]),
                    other.index
                )
                .to_optional()
            ),
            data=(
                self.data
                .combine(
                    lambda x: lambda y: dtype_concat([x, y]),
                    other.data
                )
                .to_optional()
            ),
            op=compose(other.op, self.op)
        )

    header_cstruct = np.dtype([
        ('#index', np.uint64),
        ('#oid_size', np.uint64),
        ('#result_size', np.uint64),
        ('#result_type', np.uint64),
        ('#timestamp', 'datetime64[s]')
    ])

    @property
    def oid_cstruct(self) -> np.dtype:
        # pylint: disable=no-member
        """Get the oid cstruct."""
        return (
            self.oid
            .bind(lambda x: (
                dtype_array(np.dtype(np.uint64), len(convert_oid(x)))
                .fmap(lambda arr: np.dtype([('#oid', arr)]))
            ))
            .fail(ValueError('oid has no dtype'))
        )

    def cstruct(self) -> np.dtype:
        # pylint: disable=no-member
        """Create the var_bind cstruct."""
        return dtype_concat([
            self.header_cstruct,
            self.oid_cstruct,
            *Maybe.cat([
                self.index,
                self.data
            ])
        ])

    def __call__(
            self, param: Optional[Text] = None
    ) -> Tuple[Sequence[int], Tuple[int, int]]:
        """Return a null variable binding cstruct with optional parameter."""
        return convert_oid(
            self.oid
            .combine(curry2(add), maybe_oid(param))
            .fail(AttributeError('var_bind has no oid'))
        ), (
            self.oid_cstruct.itemsize + (
                self.index
                .fmap(lambda x: x.itemsize)
                .from_maybe(0)
            ), (
                self.data
                .fmap(lambda x: x.itemsize)
                .from_maybe(0)
            )
        )
