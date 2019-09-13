"""Utility tests."""

from typing import List, Text

import hypothesis
import hypothesis.strategies as st
import pytest

from snmp_fetch.utils import align64, convert_oid, validate_oid
from tests import strategies as _st


@hypothesis.given(
    integer=st.integers()  # type: ignore
)
def test_align64(integer: int) -> None:
    """Test aligning a number to 8 bytes."""
    if integer < 0 or integer >= 2 ** 64:
        with pytest.raises(ValueError):
            align64(integer)
    else:
        aligned = align64(integer)
        assert integer == aligned or (integer >> 3) + 1 == aligned >> 3


@hypothesis.given(
    prefix=st.one_of(st.just(''), st.just('.')),  # type: ignore
    oid=_st.oids()
)
def test_convert_oid(prefix: Text, oid: List[int]) -> None:
    # pylint: disable=protected-access
    """Test converting an oid."""
    assert convert_oid(convert_oid(oid)) == oid
    assert convert_oid(prefix+'.'.join(map(str, oid))) == oid
    assert convert_oid(oid) == '.'+'.'.join(map(str, oid))


@hypothesis.given(
    oid=_st.bad_oids()  # type: ignore
)
def test_convert_bad(oid: Text) -> None:
    """Test converting a bad oid."""
    with pytest.raises(ValueError):
        convert_oid(oid)


@hypothesis.given(
    prefix=st.one_of(st.just(''), st.just('.')),  # type: ignore
    oid=_st.oids()
)
def test_validate_oid(prefix: Text, oid: List[int]) -> None:
    # pylint: disable=protected-access
    """Test validating an oid."""
    assert validate_oid(oid) == oid
    assert validate_oid(
        prefix+'.'.join(map(str, oid))
    ) == '.'+'.'.join(map(str, oid))
    assert validate_oid(oid) == oid


@hypothesis.given(
    oid=_st.bad_oids()  # type: ignore
)
def test_validate_bad_oid(oid: Text) -> None:
    # pylint: disable=protected-access
    """Test validating a bad oid."""
    with pytest.raises(ValueError):
        validate_oid(oid)
