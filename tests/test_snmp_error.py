"""SNMP error test cases."""

import pickle
from typing import Text

import hypothesis
import hypothesis.strategies as st

from snmp_fetch import SnmpError, SnmpErrorType
from tests import strategies as _st


@hypothesis.given(
    _type=_st.error_type(),  # type: ignore
    host_index=st.integers(min_value=0, max_value=(2 ** 64) - 1),
    hostname=st.text(),
    community=st.text()
)
def test_pickle_snmp_error(
        _type: SnmpErrorType,
        host_index: int,
        hostname: Text,
        community: Text
) -> None:
    """Test pickling SNMP errors."""
    snmp_error = SnmpError(_type, (host_index, hostname, community))
    assert snmp_error == pickle.loads(pickle.dumps(snmp_error))
