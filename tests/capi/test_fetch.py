# pylint: disable=ungrouped-imports  # fixed by #2824
"""Test suite for the C API."""

from typing import Sequence, Text, Tuple

import hypothesis
import hypothesis.strategies as st
import pytest

import tests.strategies as _st
from snmp_fetch import PduType, SnmpConfig, SnmpErrorType
from snmp_fetch.capi import fetch
from snmp_fetch.utils import convert_oid
from snmp_fetch.var_bind import var_bind
from tests.fixtures import snmpsimd

__all__ = ['snmpsimd']


@hypothesis.given(
    pdu_type=_st.pdu_type(),
    hosts=_st.valid_hostnames(),  # type: ignore
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
        vs = [
            var_bind(
                oid=convert_oid(oid)
            ) for oid in oids
        ]
        fetch(
            pdu_type, hosts,
            [v() for v in vs]
        )


@hypothesis.given(
    hosts=_st.valid_hostnames()
)  # type: ignore
@hypothesis.settings(
    deadline=None
)
def test_no_such_instance(
        hosts: Sequence[Tuple[int, Text, Text]]
) -> None:
    """Test ambiguous root oids."""
    results, errors = fetch(
        PduType.GET, hosts, [var_bind(oid='1')()]
    )

    print(errors)
    assert len(results) == 1
    assert results[0].size == 0
    assert len(errors) == len(hosts)
    for error in errors:
        assert error.type == SnmpErrorType.VALUE_WARNING
        assert error.message == 'NO_SUCH_INSTANCE'


@hypothesis.given(
    hosts=_st.valid_hostnames()
)  # type: ignore
@hypothesis.settings(
    deadline=None
)
def test_end_of_mib_view(
        hosts: Sequence[Tuple[int, Text, Text]]
) -> None:
    """Test ambiguous root oids."""
    config = SnmpConfig()
    results, errors = fetch(
        PduType.BULKGET, hosts, [var_bind(oid='2.0')()], config
    )

    print(errors)
    assert len(results) == 1
    assert results[0].size == 0
    assert len(errors) == len(hosts) * config.max_bulk_repetitions
    for error in errors:
        assert error.type == SnmpErrorType.VALUE_WARNING
        assert error.message == 'END_OF_MIB_VIEW'
