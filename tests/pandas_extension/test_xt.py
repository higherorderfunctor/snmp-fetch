"""SNMP config test cases."""

from typing import Sequence, Text, Tuple, Union

import hypothesis
import hypothesis.strategies as st
import numpy as np
import pandas as pd
from hypothesis.extra.numpy import arrays

from snmp_fetch.pandas_extension import xt  # pylint: disable=unused-import # noqa: F401
from snmp_fetch.pandas_extension.utils import column_names


@st.composite
def array_and_indicies(  # type: ignore
        draw, elements=st.integers(min_value=1, max_value=1000)
) -> Tuple[np.ndarray, Sequence[Union[int, slice]]]:
    """Produce 2d numpy arrays and 1d indicies into that array."""
    x = draw(elements)
    array: np.ndarray = draw(arrays(
        dtype=hypothesis.extra.numpy.unsigned_integer_dtypes('>'),
        shape=st.tuples(
            st.integers(min_value=0, max_value=1000),
            st.just(x)
        )
    ))
    indicies: Sequence[Union[int, slice]] = draw(st.lists(
        st.one_of(
            st.integers(min_value=-x, max_value=x-1),
            st.slices(size=x)  # pylint: disable=no-value-for-parameter
        ),
        min_size=1, max_size=10
    ))
    return (array, indicies)


# FUTURE: maintain index / multiindex even on series
@hypothesis.given(
    column=st.text('ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=1, max_size=2),  # type: ignore
    arr_is=array_and_indicies()  # pylint: disable=no-value-for-parameter
)
def test_get_int_item(
        column: Text,
        arr_is: Tuple[np.ndarray, Sequence[Union[int, slice]]]
) -> None:
    """Test pickling SNMP configs."""
    array, indicies = arr_is

    df = pd.DataFrame({column: [a for a in array]})  # pylint: disable=unnecessary-comprehension
    if len(indicies) == 1:
        results = df[column].xt[indicies[0]]
        assert results.name == column
        if array.shape[0] == 0:
            assert results.empty
            assert results.equals(pd.Series([a[indicies[0]] for a in array], dtype=results.dtype))
    else:
        results = df[column].xt[tuple(indicies)]
        if array.shape[0] == 0:
            assert results.empty
        else:
            safe_impl_df = pd.concat(
                [
                    df[column].apply(lambda x, i=i: x.astype(array.dtype.type)[i]).rename(n)
                    if isinstance(i, int) else
                    df[column].apply(lambda x, i=i: x.astype(array.dtype.type)[i]).rename(n)
                    for n, i in zip(column_names(len(indicies)), indicies)
                ],
                axis=1
            )
            for (a, b) in zip(results, safe_impl_df):
                if isinstance(results[a][0], np.ndarray):
                    for (c, d) in zip(results[a], safe_impl_df[b]):
                        assert np.array_equal(c, d)
                        assert c.dtype == d.dtype
                else:
                    assert results[a].equals(results[b])
