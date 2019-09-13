"""Variable bindings."""

from operator import add
from typing import Any, Callable, Optional, Sequence, Text, Tuple, Union

import attr
import numpy as np
import pandas as pd
from toolz.functoolz import compose, identity

from snmp_fetch import dtype
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
        ('host_index', np.uint64),
        ('oid_size#', np.uint64),
        ('result_size#', np.uint64),
        ('result_type#', np.uint64),
        ('timestamp', 'datetime64[s]')
    ])

    def oid_cstruct(self) -> np.dtype:
        # pylint: disable=no-member
        """Get the oid cstruct."""
        return (
            self.oid
            .bind(lambda x: (
                dtype.array(np.dtype(np.uint64), len(convert_oid(x)))
                .fmap(lambda arr: np.dtype([('oid#', arr)]))
            ))
            .fail(AttributeError('oid has no dtype'))
        )

    def index_cstruct(self, pad: bool = True) -> Maybe[np.dtype]:
        # pylint: disable=no-member
        """Get the index cstruct with optional padding."""
        return(
            self.index
            .fmap(lambda x: dtype.pad64(x, 'index#').throw() if pad else x)
        )

    def data_cstruct(self, pad: bool = True) -> Maybe[np.dtype]:
        # pylint: disable=no-member
        """Get the data cstruct with optional padding."""
        return (
            self.data
            .fmap(lambda x: dtype.pad64(x, 'data#').throw() if pad else x)
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
        df = pd.DataFrame.from_records(
            view.tolist(), columns=view.dtype.names
        )
        df = df[~df['result_type#'].isin([128, 129, 130])]
        df = self.op(df)  # pylint: disable=not-callable
        df = df.drop(columns=({
            'oid#', 'oid_size#', 'result_size#', 'result_type#', 'index#',
            'data#', 'mask'
        }.intersection(df.columns)))
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
        return df


def merge_results(
        results: np.ndarray, var_binds: Sequence[var_bind],
        extras: Optional[Any] = None,
        index: Union[Text, Sequence[Text]] = 'host_index'
) -> Optional[Any]:
    """Merge result variable bindings."""
    df = None
    for v, result in zip(var_binds, results):
        if result.size == 0:
            continue
        _df = v.view(result)
        if df is None:
            df = _df
        else:
            df = df.merge(
                _df, how='outer', left_index=True, right_index=True,
                sort=True
            )
            # Hitting an issue when a row enters/leaves mid collection which
            # results in an NaT in the timestamp column for the column missing
            # row data on merge.  Running max with the NaT value causes the
            # entire timestamp column to fill with NaN.  To avoid this, NaT's
            # are filled with the max timestamp value in the respective column
            # prior to getting the max value.
            for tkey in ['timestamp_x', 'timestamp_y']:
                df[tkey] = df[tkey].fillna(df[tkey].max())
            df['timestamp'] = df[['timestamp_x', 'timestamp_y']].max(axis=1)
            df = df.drop(columns=['timestamp_x', 'timestamp_y'])
    if df is not None:
        df = df.reset_index()
        if extras is not None:
            df = (
                df.set_index(index)
                .merge(
                    extras.set_index(index), how='left', left_index=True,
                    right_index=True
                )
                .reset_index()
                .drop(columns='host_index')
            )
    return df
