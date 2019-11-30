# pylint: disable=ungrouped-imports  # fixed by #2824
"""Test suite for the C API."""

from typing import Sequence, Text, Tuple

import hypothesis
import hypothesis.strategies as st
import pytest

import tests.strategies as _st
from snmp_fetch import PduType, SnmpConfig, SnmpErrorType
from snmp_fetch.api import snmp
from tests.fixtures import snmpsimd

__all__ = ['snmpsimd']


@hypothesis.given(
    pdu_type=_st.pdu_types(),
    hosts=_st.valid_hosts(),  # type: ignore
    oids=st.lists(st.one_of([
        st.just((1, 3, 6, 1, 2, 1, 1, 3)),
        st.just((1, 3, 6, 1, 2, 1, 1, 3, 0))
    ]), min_size=2)
)
@hypothesis.settings(
    deadline=None
)
def test_ambiguous_root_oids(
        pdu_type: PduType,
        hosts: Sequence[Tuple[int, Text, Text]],
        oids: Sequence[Sequence[int]]
) -> None:
    """Test ambiguous root oids."""
    with pytest.raises(ValueError):
        snmp(
            pdu_type, hosts,
            [(oid, (0, 0)) for oid in oids]
        )


@hypothesis.given(
    hosts=_st.valid_hosts()
)  # type: ignore
@hypothesis.settings(
    deadline=None
)
def test_no_such_instance(
        hosts: Sequence[Tuple[int, Text, Text]]
) -> None:
    """Test no such instance."""
    results, errors = snmp(
        PduType.GET, hosts, [([1], (0, 0))]
    )

    assert len(results) == 1
    assert results[0].size == 0
    assert len(errors) == len(hosts)
    for error in errors:
        assert error.type == SnmpErrorType.VALUE_WARNING
        assert error.message == 'NO_SUCH_INSTANCE'


@hypothesis.given(
    hosts=_st.valid_hosts()
)  # type: ignore
@hypothesis.settings(
    deadline=None
)
def test_end_of_mib_view(
        hosts: Sequence[Tuple[int, Text, Text]]
) -> None:
    """Test end of MIB view."""
    config = SnmpConfig()
    results, errors = snmp(
        PduType.BULKGET, hosts, [([2, 0], (0, 0))]
    )

    assert len(results) == 1
    assert results[0].size == 0
    assert len(errors) == len(hosts) * config.max_bulk_repetitions
    for error in errors:
        assert error.type == SnmpErrorType.VALUE_WARNING
        assert error.message == 'END_OF_MIB_VIEW'
