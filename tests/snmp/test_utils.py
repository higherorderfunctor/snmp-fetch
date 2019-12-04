"""Variable binding tests."""

import re
from typing import List, Text

import hypothesis
import hypothesis.strategies as st
import pytest

from snmp_fetch.snmp.utils import validate_oid
from .strategies import oids


@hypothesis.given(
    prefix=st.one_of(st.just(''), st.just('.')),  # type: ignore
    oid=oids()
)
def test_validate_oid(prefix: Text, oid: List[int]) -> None:
    """Test validating an oid."""
    assert validate_oid(oid) == oid
    assert validate_oid(
        prefix+'.'.join(map(str, oid))
    ) == '.'+'.'.join(map(str, oid))
    assert validate_oid(oid) == oid


@hypothesis.given(
    oid=st.text().filter(  # type: ignore
        lambda x: re.match(r'^\.?\d+(\.\d+)*$', x) is None
    )
)
def test_validate_invalid_oid(oid: Text) -> None:
    """Test validating an invalid oid."""
    with pytest.raises(ValueError):
        validate_oid(oid)
