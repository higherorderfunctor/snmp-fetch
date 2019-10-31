"""Test composable DataFrame functions."""

import hypothesis
import hypothesis.strategies as st
import pandas as pd
from hypothesis.extra import pandas as df_st

from snmp_fetch.df.functions import astype, decode, set_index, to_timedelta


@hypothesis.given(
    df=df_st.data_frames([  # type: ignore
        df_st.column('A', dtype=pd.np.uint64),
        df_st.column('B', dtype=float)
    ])
)
def test_set_index(df) -> None:
    """Test set_index."""
    assert df.set_index('A').index.equals(set_index('A')(df).index)


@hypothesis.given(
    df=df_st.data_frames([  # type: ignore
        df_st.column('A', dtype=pd.np.uint64)
    ])
)
def test_as_type(df) -> None:
    """Test astype."""
    assert df['A'].astype(pd.UInt64Dtype()).equals(
        astype('A', pd.UInt64Dtype())(df)['A']
    )


@hypothesis.given(
    rows=st.text()  # type: ignore
)
def test_decode(rows) -> None:
    """Test decode."""
    df = pd.DataFrame(data=[s.encode() for s in rows], columns=['A'])
    assert df['A'].str.decode('utf-8', errors='ignore').equals(decode('A')(df)['A'])


@hypothesis.given(
    rows=st.lists(st.timedeltas(), min_size=1)  # type: ignore
)
def test_to_timedelta(rows) -> None:
    """Test to_timedelta."""
    df = pd.DataFrame(data=[dt.seconds for dt in rows], columns=['A'])
    assert pd.to_timedelta(df['A'], unit='seconds').equals(to_timedelta('A')(df)['A'])
