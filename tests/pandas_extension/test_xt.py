"""SNMP config test cases."""

from typing import Any, Sequence, Text, Tuple, Union, cast

import hypothesis
import hypothesis.strategies as st
import numpy as np
import pandas as pd
from hypothesis.extra.numpy import arrays, integer_dtypes
from hypothesis.extra.pandas import indexes
from hypothesis.searchstrategy.strategies import SearchStrategy

from snmp_fetch.pandas_extension import xt  # pylint: disable=unused-import # noqa: F401
from snmp_fetch.pandas_extension.utils import column_names


def index_and_array_and_items(
        num_columns: SearchStrategy[int] = st.integers(min_value=1, max_value=10),
        num_rows: SearchStrategy[int] = st.integers(min_value=0, max_value=1000)
) -> SearchStrategy[Tuple[
    Any,
    np.ndarray,
    Sequence[Union[int, slice]]
]]:
    """Produce 2d numpy arrays and 1d indicies into that array."""
    return num_columns.flatmap(lambda cols: num_rows.flatmap(lambda rows: cast(
        SearchStrategy[Tuple[Any, np.ndarray, Sequence[Union[int, slice]]]],
        integer_dtypes().flatmap(lambda dtype: st.tuples(
            st.one_of(
                indexes(dtype=dtype, min_size=rows, max_size=rows, unique=False),
                st.builds(
                    lambda a, b: pd.MultiIndex.from_arrays([a, b]),
                    indexes(dtype=dtype, min_size=rows, max_size=rows, unique=False),
                    indexes(dtype=dtype, min_size=rows, max_size=rows, unique=False),
                )
            ),
            arrays(
                dtype=hypothesis.extra.numpy.unsigned_integer_dtypes('>'),
                shape=st.tuples(
                    st.just(rows),
                    st.just(cols)
                )
            ),
            st.lists(
                st.one_of(
                    st.integers(min_value=-cols, max_value=cols-1),
                    st.slices(size=cols)  # pylint: disable=no-value-for-parameter
                ),
                min_size=1, max_size=10
            )
        ))
    )))


@hypothesis.given(
    column=st.text('ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=1, max_size=2),  # type: ignore
    index_array_items=index_and_array_and_items()
)
def test_get_int_item(
        column: Text,
        index_array_items: Tuple[Any, np.ndarray, Sequence[Union[int, slice]]]
) -> None:
    """Test pickling SNMP configs."""
    index, array, items = index_array_items

    df = pd.DataFrame({column: list(array)})
    df.index = index
    if len(items) == 1:
        results = df[column].xt[items[0]]
        assert results.index.equals(index)
        assert results.name == column
        if array.shape[0] == 0:
            assert results.empty
            assert results.equals(pd.Series([a[items[0]] for a in array], dtype=results.dtype))
    else:
        results = df[column].xt[tuple(items)]
        assert results.index.equals(index)
        if array.shape[0] == 0:
            assert results.empty
        else:
            safe_impl_df = pd.concat(
                [
                    df[column].apply(lambda x, i=i: x.astype(array.dtype.type)[i]).rename(n)
                    if isinstance(i, int) else
                    df[column].apply(lambda x, i=i: x.astype(array.dtype.type)[i]).rename(n)
                    for n, i in zip(column_names(len(items)), items)
                ],
                axis=1
            )
            for (a, b) in zip(results, safe_impl_df):
                if isinstance(results[a].iloc[0], np.ndarray):
                    for (c, d) in zip(results[a], safe_impl_df[b]):
                        assert np.array_equal(c, d)
                        assert c.dtype == d.dtype
                else:
                    assert results[a].equals(results[b])
