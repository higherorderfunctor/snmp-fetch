"""Variable binding tests."""

from typing import List, Text

import hypothesis
import hypothesis.strategies as st
import pytest

from snmp_fetch.utils import validate_oid
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
