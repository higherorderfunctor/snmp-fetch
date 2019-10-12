"""Hypothesis strategies."""

import re
import string
from typing import Any, List, Sequence, Text

import hypothesis
import hypothesis.strategies as st
import numpy as np

from snmp_fetch import PduType, SnmpErrorType

VALID_HOSTNAMES = [
    '127.0.0.1:1161',  # IPv4
    '[::1]:1161',      # IPv6
    'localhost:1161',  # DNS resolution
    ':1161'            # auto fill localhost
]


INVALID_HOSTNAMES = [
    '*', '0'
]


INVALID_HOSTS: List[Any] = [
    0,
    None,
    [],
    tuple(),
    '127.0.0.1:1161',
    ('127.0.0.1:1161',),
    (0, '127.0.0.1:1161',),
    ('127.0.0.1:1161', None),
    (None, 'public'),
    (None, None),
]


TIMEOUT_HOSTNAMES = [
    '127.0.0.1:1234',  # IPv4
    '[::1]:1234',      # IPv6
    'localhost:1234',  # DNS resolution
    ':1234',           # auto fill localhost
    ''                 # auto fill localhost and port
]

VALID_COMMUNITIES = [
    'recorded/linux-full-walk'
]


def create_hosts_strategy(
        hostnames: Sequence[Text],
        communities: Sequence[Text],
) -> hypothesis.searchstrategy.strategies.SearchStrategy[Any]:
    """Generate a list of test hosts."""
    return st.lists(st.tuples(
        st.integers(min_value=0, max_value=(2 ** 64) - 1),
        st.one_of([st.just(host) for host in hostnames]),
        st.one_of([st.just(community) for community in communities]),
    ), min_size=1)


def valid_hostnames() -> (
        hypothesis.searchstrategy.strategies.SearchStrategy[Any]
):
    """Generate valid testing hostnames."""
    return create_hosts_strategy(
        VALID_HOSTNAMES,
        VALID_COMMUNITIES
    )


def invalid_hostnames() -> (
        hypothesis.searchstrategy.strategies.SearchStrategy[Any]
):
    """Generate invalid testing hostnames."""
    return create_hosts_strategy(
        INVALID_HOSTNAMES,
        VALID_COMMUNITIES
    )


def timeout_hostnames() -> (
        hypothesis.searchstrategy.strategies.SearchStrategy[Any]
):
    """Generate timeout testing hostnames."""
    return create_hosts_strategy(
        TIMEOUT_HOSTNAMES,
        VALID_COMMUNITIES
    )


def dtype() -> hypothesis.searchstrategy.strategies.SearchStrategy[Any]:
    """Generate a dtype."""
    return st.one_of([
        st.just(np.uint8),
        st.just(np.uint16),
        st.just(np.uint32),
        st.just(np.uint64),
        st.just(np.dtype('S255')),
        st.just(np.dtype('S256'))
    ])


def dtype_struct() -> hypothesis.searchstrategy.strategies.SearchStrategy[Any]:
    """Generate a structued dtype."""
    return st.lists(st.tuples(
        st.text(alphabet=string.ascii_letters, min_size=1),
        dtype()
    ), min_size=1, unique_by=lambda x: x[0])


def pdu_type() -> hypothesis.searchstrategy.strategies.SearchStrategy[PduType]:
    """Generate a PDU type."""
    return st.one_of([
        st.just(PduType.GET_REQUEST),
        st.just(PduType.NEXT_REQUEST),
        st.just(PduType.BULKGET_REQUEST)
    ])


def oids() -> (
        hypothesis.searchstrategy.strategies.SearchStrategy[Sequence[int]]
):
    """Generate integer oids."""
    return st.lists(
        st.integers(min_value=0, max_value=2 ^ 64 - 1), min_size=1
    )


def bad_oids() -> hypothesis.searchstrategy.strategies.SearchStrategy[Text]:
    """Generate bad text oids."""
    return st.text().filter(
        lambda x: re.match(r'^\.?\d+(\.\d+)*$', x) is None
    )


def error_type() -> (
        hypothesis.searchstrategy.strategies.SearchStrategy[SnmpErrorType]
):
    """Generate a PDU type."""
    return st.one_of([
        st.just(SnmpErrorType.SESSION_ERROR),
        st.just(SnmpErrorType.CREATE_REQUEST_PDU_ERROR),
        st.just(SnmpErrorType.SEND_ERROR),
        st.just(SnmpErrorType.BAD_RESPONSE_PDU_ERROR),
        st.just(SnmpErrorType.TIMEOUT_ERROR),
        st.just(SnmpErrorType.ASYNC_PROBE_ERROR),
        st.just(SnmpErrorType.TRANSPORT_DISCONNECT_ERROR),
        st.just(SnmpErrorType.CREATE_RESPONSE_PDU_ERROR),
    ])
