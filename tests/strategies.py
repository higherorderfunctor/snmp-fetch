"""Hypothesis strategies."""

import re
import string
from typing import Sequence, Text, Tuple, cast

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


def hosts(
        hostnames: Sequence[Text],
        communities: Sequence[Text],
) -> hypothesis.searchstrategy.strategies.SearchStrategy[Sequence[Tuple[int, Text, Text]]]:
    """Generate a list of test hosts."""
    return st.lists(
        cast(
            hypothesis.searchstrategy.strategies.SearchStrategy[Tuple[int, Text, Text]],
            st.tuples(
                st.integers(min_value=0, max_value=(2 ** 64) - 1),
                st.one_of([st.just(host) for host in hostnames]),
                st.one_of([st.just(community) for community in communities])
            )
        ), min_size=1
    )


def valid_hosts() -> (
        hypothesis.searchstrategy.strategies.SearchStrategy[Sequence[Tuple[int, Text, Text]]]
):
    """Generate valid testing hostnames."""
    return hosts(
        VALID_HOSTNAMES,
        VALID_COMMUNITIES
    )


def invalid_hosts() -> (
        hypothesis.searchstrategy.strategies.SearchStrategy[Sequence[Tuple[int, Text, Text]]]
):
    """Generate invalid testing hostnames."""
    return hosts(
        INVALID_HOSTNAMES,
        VALID_COMMUNITIES
    )


def timeout_hosts() -> (
        hypothesis.searchstrategy.strategies.SearchStrategy[Sequence[Tuple[int, Text, Text]]]
):
    """Generate timeout testing hostnames."""
    return hosts(
        TIMEOUT_HOSTNAMES,
        VALID_COMMUNITIES
    )


def dtypes() -> hypothesis.searchstrategy.strategies.SearchStrategy[np.dtype]:
    """Generate a dtype."""
    return st.one_of([
        st.just(np.dtype((np.uint8, 8))),
        st.just(np.dtype((np.uint16, 4))),
        st.just(np.dtype((np.uint32, 2))),
        st.just(np.uint64),
        st.just(np.dtype('S256'))
    ])


def dtype_structs() -> (
        hypothesis.searchstrategy.strategies.SearchStrategy[Sequence[Tuple[Text, np.dtype]]]
):
    """Generate a structued dtype."""
    return st.lists(
        cast(
            hypothesis.searchstrategy.strategies.SearchStrategy[Tuple[Text, np.dtype]],
            st.tuples(
                st.text(alphabet=string.ascii_letters, min_size=1),
                dtypes()
            )
        ), min_size=1, unique_by=lambda x: x[0]
    )


def pdu_types() -> hypothesis.searchstrategy.strategies.SearchStrategy[PduType]:
    """Generate a PDU type."""
    return st.one_of([
        st.just(PduType.GET),
        st.just(PduType.NEXT),
        st.just(PduType.BULKGET)
    ])


def oids() -> (
        hypothesis.searchstrategy.strategies.SearchStrategy[Sequence[int]]
):
    """Generate valid integer oids."""
    return st.lists(
        st.integers(min_value=0, max_value=2 ^ 64 - 1), min_size=1, max_size=128
    )


def invalid_oids() -> hypothesis.searchstrategy.strategies.SearchStrategy[Text]:
    """Generate invalid text oids."""
    return st.text().filter(
        lambda x: re.match(r'^\.?\d+(\.\d+)*$', x) is None
    )


def error_types() -> (
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
        st.just(SnmpErrorType.VALUE_WARNING),
    ])
