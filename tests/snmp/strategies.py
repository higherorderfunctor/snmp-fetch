"""Netframe SNMP Hypothesis strategies."""

from typing import Optional, TypeVar

import hypothesis.strategies as st
from hypothesis.searchstrategy.strategies import SearchStrategy

from snmp_fetch.snmp.api import (
    Community, Config, Host, NullVarBind, ObjectIdentityParameter, PduType, SnmpError,
    SnmpErrorType, Version
)
from snmp_fetch.snmp.types import ObjectIdentity

T = TypeVar('T')


def optionals(strategy: SearchStrategy[T]) -> SearchStrategy[Optional[T]]:
    """Generate an optional strategy."""
    return st.one_of(
        st.none(), strategy
    )


def int64s() -> SearchStrategy[int]:
    """Generate an int64."""
    return st.integers(
        min_value=-(2 ^ 63),
        max_value=(2 ^ 63) - 1
    )


def uint64s() -> SearchStrategy[int]:
    """Generate a uint64."""
    return st.integers(
        min_value=0,
        max_value=(2 ^ 64) - 1
    )


def oids() -> SearchStrategy[ObjectIdentity]:
    """Generate an ObjectIdentity."""
    return st.lists(uint64s(), min_size=1, max_size=128)


def pdu_types() -> SearchStrategy[PduType]:
    """Generate a PduType."""
    return st.one_of([
        st.just(PduType.GET),
        st.just(PduType.NEXT),
        st.just(PduType.BULKGET)
    ])


def null_var_binds() -> SearchStrategy[NullVarBind]:
    """Generate a NullVarBind."""
    return st.builds(
        NullVarBind,
        oid=oids(),
        oid_size=uint64s(),
        value_size=uint64s()
    )


def configs() -> SearchStrategy[Config]:
    """Generate a Config."""
    return st.builds(
        Config,
        retries=int64s(),
        timeout=int64s(),
        var_binds_per_pdu=uint64s(),
        bulk_repetitions=uint64s()
    )


def object_identity_parameters() -> SearchStrategy[ObjectIdentityParameter]:
    """Generate an ObjectIdentityParameter."""
    return st.builds(
        ObjectIdentityParameter,
        start=oids(),
        end=optionals(oids())
    )


def versions() -> SearchStrategy[Version]:
    """Generate a Version."""
    return st.one_of([
        st.just(Version.V2C)
    ])


def communities() -> SearchStrategy[Community]:
    """Generate a Community."""
    return st.builds(
        Community,
        index=uint64s(),
        version=st.just(Version.V2C),
        string=st.text()
    )


def hosts() -> SearchStrategy[Host]:
    """Generate a Host."""
    return st.builds(
        Host,
        index=uint64s(),
        hostname=st.text(),
        communities=st.lists(communities()),
        parameters=optionals(st.lists(object_identity_parameters())),
        config=st.one_of(st.none(), configs())
    )


def snmp_error_types() -> SearchStrategy[SnmpErrorType]:
    """Generate an SnmpErrorType."""
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


def snmp_errors() -> SearchStrategy[Host]:
    """Generate an SnmpError."""
    return st.builds(
        SnmpError,
        type=snmp_error_types(),
        sys_errno=optionals(int64s()),
        snmp_errno=optionals(int64s()),
        err_stat=optionals(int64s()),
        err_index=optionals(int64s()),
        err_oid=optionals(oids()),
        message=optionals(st.text())
    )


########################
# 
# 
# VALID_HOSTNAMES = [
#     '127.0.0.1:1161',  # IPv4
#     '[::1]:1161',      # IPv6
#     'localhost:1161',  # DNS resolution
#     ':1161'            # auto fill localhost
# ]
# 
# 
# INVALID_HOSTNAMES = [
#     '*', '0'
# ]
# 
# 
# TIMEOUT_HOSTNAMES = [
#     '127.0.0.1:1234',  # IPv4
#     '[::1]:1234',      # IPv6
#     'localhost:1234',  # DNS resolution
#     ':1234',           # auto fill localhost
#     ''                 # auto fill localhost and port
# ]
# 
# VALID_COMMUNITIES = [
#     'recorded/linux-full-walk'
# ]
# 
# 
# def valid_hosts() -> (
#         hypothesis.searchstrategy.strategies.SearchStrategy[Sequence[Tuple[int, Text, Text]]]
# ):
#     """Generate valid testing hostnames."""
#     return hosts(
#         VALID_HOSTNAMES,
#         VALID_COMMUNITIES
#     )
# 
# 
# def invalid_hosts() -> (
#         hypothesis.searchstrategy.strategies.SearchStrategy[Sequence[Tuple[int, Text, Text]]]
# ):
#     """Generate invalid testing hostnames."""
#     return hosts(
#         INVALID_HOSTNAMES,
#         VALID_COMMUNITIES
#     )
# 
# 
# def timeout_hosts() -> (
#         hypothesis.searchstrategy.strategies.SearchStrategy[Sequence[Tuple[int, Text, Text]]]
# ):
#     """Generate timeout testing hostnames."""
#     return hosts(
#         TIMEOUT_HOSTNAMES,
#         VALID_COMMUNITIES
#     )
# 
# 
# def dtypes() -> hypothesis.searchstrategy.strategies.SearchStrategy[np.dtype]:
#     """Generate a dtype."""
#     return st.one_of([
#         st.just(np.dtype((np.uint8, 8))),
#         st.just(np.dtype((np.uint16, 4))),
#         st.just(np.dtype((np.uint32, 2))),
#         st.just(np.uint64),
#         st.just(np.dtype('S256'))
#     ])
# 
# 
# def dtype_structs() -> (
#         hypothesis.searchstrategy.strategies.SearchStrategy[Sequence[Tuple[Text, np.dtype]]]
# ):
#     """Generate a structued dtype."""
#     return st.lists(
#         cast(
#             hypothesis.searchstrategy.strategies.SearchStrategy[Tuple[Text, np.dtype]],
#             st.tuples(
#                 st.text(alphabet=string.ascii_letters, min_size=1),
#                 dtypes()
#             )
#         ), min_size=1, unique_by=lambda x: x[0]
#     )
# 
# 
# 
# 
# 
# 
# def invalid_text_oids() -> hypothesis.searchstrategy.strategies.SearchStrategy[Text]:
#     """Generate invalid text oids."""
#     return st.text().filter(
#         lambda x: re.match(r'^\.?\d+(\.\d+)*$', x) is None
#     )
# 
# 
