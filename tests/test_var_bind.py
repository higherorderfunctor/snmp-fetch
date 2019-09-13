"""Variable binding tests."""

from typing import List, Text

import hypothesis
import hypothesis.strategies as st
import numpy as np
import pytest

from snmp_fetch.fp.maybe import Just, Nothing
from snmp_fetch.var_bind import var_bind
from tests import strategies as _st


@hypothesis.given(
    prefix=st.one_of(st.just(''), st.just('.')),  # type: ignore
    oid=_st.oids()
)
def test_oid_var_bind(prefix: Text, oid: List[int]) -> None:
    # pylint: disable=protected-access
    """Test oid only variable binding."""
    v = var_bind(
        oid=prefix+'.'.join(map(str, oid))
    )
    assert v.oid == Just('.'+'.'.join(map(str, oid)))
    assert v.index == Nothing()
    assert v.data == Nothing()


@hypothesis.given(
    oid=_st.bad_oids()  # type: ignore
)
def test_oid_var_bind_with_invalid_input(oid) -> None:
    # pylint: disable=protected-access
    """Test oid variable binding with invalid input."""
    with pytest.raises(ValueError):
        var_bind(
            oid=oid
        )


@hypothesis.given(
    dtype=_st.dtype_struct()  # type: ignore
)
def test_index_var_bind(dtype) -> None:
    # pylint: disable=protected-access, no-member
    """Test index variable binding."""
    v = var_bind(
        index=np.dtype(dtype)
    )
    assert v.oid == Nothing()
    assert v.index == Just(np.dtype(dtype))
    assert v.data == Nothing()


@hypothesis.given(
    dtype=_st.dtype_struct()  # type: ignore
)
def test_data_var_bind(dtype) -> None:
    # pylint: disable=protected-access, no-member
    """Test data variable binding."""
    v = var_bind(
        data=np.dtype(dtype)
    )
    assert v.oid == Nothing()
    assert v.index == Nothing()
    assert v.data == Just(np.dtype(dtype))
