"""Variable bindings."""

from operator import add
from typing import Any, Callable, Optional, Sequence, Text, Tuple

import attr
import numpy as np
import pandas as pd
from toolz.functoolz import compose, identity

from . import dtype
from .fp import curry2
from .fp.maybe import Maybe
from .utils import convert_oid, validate_oid


def maybe_oid(oid: Optional[Text]) -> Maybe[Text]:
    """Validate and wrap an oid in a Maybe."""
    return Maybe.from_optional(oid).fmap(validate_oid)


@attr.s(frozen=True, slots=True)
class var_bind:
    # pylint: disable=invalid-name
    """Variable binding."""

    oid: Maybe[Text] = attr.ib(
        default=None, converter=maybe_oid
    )
    index: Maybe[np.dtype] = attr.ib(
        default=None, converter=dtype.to_dtype
    )
    data: Maybe[np.dtype] = attr.ib(
        default=None, converter=dtype.to_dtype
    )
    op: Callable[[Any], Any] = attr.ib(
        default=identity
    )

    def __lshift__(self, other: 'var_bind') -> 'var_bind':
        # pylint: disable=no-member
        """Combine variable bindings."""
        return var_bind(
            oid=(
                self.oid
                .combine(curry2(add), other.oid)
                .to_optional()
            ),
            index=(
                self.index
                .combine(
                    lambda x: lambda y: dtype.concatv(x, y).throw(),
                    other.index
                )
                .to_optional()
            ),
            data=(
                self.data
                .combine(
                    lambda x: lambda y: dtype.concatv(x, y).throw(),
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

    def oid_cstruct(self) -> np.dtype:
        # pylint: disable=no-member
        """Get the oid cstruct."""
        return (
            self.oid
            .bind(lambda x: (
                dtype.array(np.dtype(np.uint64), len(convert_oid(x)))
                .fmap(lambda arr: np.dtype([('#oid', arr)]))
            ))
            .fail(AttributeError('oid has no dtype'))
        )

    def index_cstruct(self, pad: bool = True) -> Maybe[np.dtype]:
        # pylint: disable=no-member
        """Get the index cstruct with optional padding."""
        return(
            self.index
            .fmap(lambda x: dtype.pad64(x, '#ipadding').throw() if pad else x)
        )

    def data_cstruct(self, pad: bool = True) -> Maybe[np.dtype]:
        # pylint: disable=no-member
        """Get the data cstruct with optional padding."""
        return (
            self.data
            .fmap(lambda x: dtype.pad64(x, '#dpadding').throw() if pad else x)
        )

    def cstruct(self) -> np.dtype:
        # pylint: disable=no-member
        """Create the var_bind cstruct."""
        return dtype.concat([
            self.header_cstruct,
            self.oid_cstruct(),
            *Maybe.cat([
                self.index_cstruct(),
                self.data_cstruct()
            ])
        ]).throw()

    def null_cstruct(
            self, param: Optional[Text] = None
    ) -> Tuple[Sequence[int], Tuple[int, int]]:
        # pylint: disable=no-member
        """Return a null variable binding cstruct with optional parameter."""
        return convert_oid(
            self.oid
            .combine(curry2(add), maybe_oid(param))
            .fail(AttributeError('var_bind has no oid'))
        ), (
            self.oid_cstruct().itemsize + (
                self.index_cstruct(pad=False)
                .fmap(lambda x: x.itemsize)
                .from_maybe(0)
            ), (
                self.data_cstruct(pad=False)
                .fmap(lambda x: x.itemsize)
                .from_maybe(0)
            )
        )

    def __call__(
            self, param: Optional[Text] = None
    ) -> Tuple[Sequence[int], Tuple[int, int]]:
        """Return a null variable binding cstruct with optional parameter."""
        return self.null_cstruct(param)

    def view(self, arr: np.ndarray) -> Any:
        # pylint: disable=no-member
        """Convert a cstruct array to a dataframe."""
        view = arr.view(self.cstruct())
        df = pd.DataFrame(
            view.tolist(), columns=view.dtype.names
        )
        df = self.op(df)  # pylint: disable=not-callable
        df = df.drop(columns=({
            '#index', '#oid_size', '#result_size', '#result_type', '#oid', '#timestamp',
            '#ipadding', '#dpadding'
        }.intersection(df.columns)))
        df['#timestamp'] = df['#timestamp'].dt.tz_localize('UTC')
        return df
