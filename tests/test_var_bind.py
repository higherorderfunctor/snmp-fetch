"""Variable binding tests."""

from typing import List, Text

import hypothesis
import hypothesis.strategies as st
import numpy as np
import pytest

from snmp_fetch.fp.maybe import Just, Nothing
from snmp_fetch.var_bind import VarBind, validate_oid
from tests import strategies as _st


@hypothesis.given(
    prefix=st.one_of(st.just(''), st.just('.')),  # type: ignore
    oid=_st.oids()
)
def test_validate_oid(prefix: Text, oid: List[int]) -> None:
    """Test validating an oid."""
    assert validate_oid(oid) == oid
    assert validate_oid(
        prefix+'.'.join(map(str, oid))
    ) == '.'+'.'.join(map(str, oid))
    assert validate_oid(oid) == oid


@hypothesis.given(
    oid=_st.invalid_oids()  # type: ignore
)
def test_validate_invalid_oid(oid: Text) -> None:
    """Test validating an invalid oid."""
    with pytest.raises(ValueError):
        validate_oid(oid)


@hypothesis.given(
    prefix=st.one_of(st.just(''), st.just('.')),  # type: ignore
    oid=_st.oids()
)
def test_oid_var_bind(prefix: Text, oid: List[int]) -> None:
    # pylint: disable=protected-access
    """Test oid only variable binding."""
    v = VarBind(
        oid=prefix+'.'.join(map(str, oid))
    )
    assert v.oid == Just('.'+'.'.join(map(str, oid)))
    assert v.index == Nothing()
    assert v.data == Nothing()


@hypothesis.given(
    oid=_st.invalid_oids()  # type: ignore
)
def test_oid_var_bind_with_invalid_input(oid) -> None:
    """Test oid variable binding with invalid input."""
    with pytest.raises(ValueError):
        VarBind(
            oid=oid
        )


@hypothesis.given(
    dtype=_st.dtype_structs()  # type: ignore
)
def test_index_var_bind(dtype) -> None:
    """Test index variable binding."""
    v = VarBind(
        index=np.dtype(dtype)
    )
    assert v.oid == Nothing()
    assert v.index == Just(np.dtype(dtype))
    assert v.data == Nothing()


@hypothesis.given(
    dtype=_st.dtype_structs()  # type: ignore
)
def test_data_var_bind(dtype) -> None:
    """Test data variable binding."""
    v = VarBind(
        data=np.dtype(dtype)
    )
    assert v.oid == Nothing()
    assert v.index == Nothing()
    assert v.data == Just(np.dtype(dtype))
