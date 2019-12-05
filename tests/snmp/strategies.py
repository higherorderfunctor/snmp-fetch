"""Netframe SNMP Hypothesis strategies."""

from collections.abc import Sequence as AbstractSequence
from typing import Optional, Sequence, Text, TypeVar, Union

import hypothesis.strategies as st
from hypothesis.searchstrategy.strategies import SearchStrategy

from snmp_fetch.snmp.api import (
    Community, Config, Host, NullVarBind, ObjectIdentityParameter, PduType, SnmpError,
    SnmpErrorType, Version
)
from snmp_fetch.snmp.types import ObjectIdentity

T = TypeVar('T')


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


def optionals(strategy: SearchStrategy[T]) -> SearchStrategy[Optional[T]]:
    """Generate an optional strategy."""
    return st.one_of(
        st.none(), strategy
    )


def int64s(
        min_value: int = -(2 ** 63),
        max_value: int = (2 ** 63) - 1
) -> SearchStrategy[int]:
    """Generate an int64."""
    if min_value > max_value:
        raise TypeError('min_value must be less than or equal max_value.')
    if min_value < -(2 ** 63):
        raise TypeError(f'min_value must be greater than or equal to {-(2 ** 63)}.')
    if min_value > (2 ** 63) - 1:
        raise TypeError(f'min_value must be less than or equal to {(2 ** 63) - 1}.')
    if max_value < -(2 ** 63):
        raise TypeError(f'max_value must be greater than or equal to {-(2 ** 63)}.')
    if max_value > (2 ** 63) - 1:
        raise TypeError(f'max_value must be less than or equal to {(2 ** 63) - 1}.')
    return st.integers(
        min_value,
        max_value
    )


def uint64s(
        min_value: int = 0,
        max_value: int = (2 ** 64) - 1
) -> SearchStrategy[int]:
    """Generate a uint64."""
    if min_value > max_value:
        raise TypeError('min_value must be less than or equal to max_value.')
    if min_value < 0:
        raise TypeError('min_value must be greater than or equal to 0.')
    if min_value > (2 ** 64) - 1:
        raise TypeError(f'min_value must be less than or equal to {(2 ** 64) - 1}.')
    if max_value < 0:
        raise TypeError('max_value must be greater than or equal to 0.')
    if max_value > (2 ** 64) - 1:
        raise TypeError(f'max_value must be less than or equal to {(2 ** 64) - 1}.')
    return st.integers(
        min_value,
        max_value
    )


def oids(
        min_size: int = 1,
        max_size: int = 128,
        prefix: Optional[ObjectIdentity] = None
) -> SearchStrategy[ObjectIdentity]:
    """Generate an ObjectIdentity."""
    if prefix is None:
        prefix = []
    return st.builds(
        lambda x: prefix + x,
        st.lists(uint64s(), min_size=min_size, max_size=max_size)
    )


def pdu_types(
        types: Optional[Sequence[PduType]] = None
) -> SearchStrategy[PduType]:
    """Generate a PduType."""
    if types is None:
        _types = [
            st.just(PduType.GET),
            st.just(PduType.NEXT),
            st.just(PduType.BULKGET)
        ]
    else:
        _types = [st.just(t) for t in types]
    return st.one_of(_types)


def null_var_binds(
        oid: SearchStrategy[ObjectIdentity] = oids(),
        oid_size: SearchStrategy[int] = uint64s(),
        value_size: SearchStrategy[int] = uint64s()
) -> SearchStrategy[NullVarBind]:
    """Generate a NullVarBind."""
    return st.builds(
        NullVarBind,
        oid,
        oid_size,
        value_size
    )


def configs(
        retries: SearchStrategy[int] = int64s(min_value=0, max_value=1),
        timeout: SearchStrategy[int] = int64s(min_value=0, max_value=1),
        var_binds_per_pdu: SearchStrategy[int] = uint64s(min_value=1, max_value=10),
        bulk_repetitions: SearchStrategy[int] = int64s(min_value=0, max_value=10)
) -> SearchStrategy[Config]:
    """Generate a Config."""
    return st.builds(
        Config,
        retries,
        timeout,
        var_binds_per_pdu,
        bulk_repetitions
    )


def object_identity_parameters(
        start: SearchStrategy[Optional[ObjectIdentity]] = optionals(oids()),
        end: SearchStrategy[Optional[ObjectIdentity]] = optionals(oids())
) -> SearchStrategy[ObjectIdentityParameter]:
    """Generate an ObjectIdentityParameter."""
    return st.builds(
        ObjectIdentityParameter,
        start,
        end
    )


def versions() -> SearchStrategy[Version]:
    """Generate a Version."""
    return st.one_of([
        st.just(Version.V2C)
    ])


def communities(
        version: SearchStrategy[Version] = st.just(Version.V2C),
        string: Union[SearchStrategy[Text], Sequence[Text]] = st.text()
) -> SearchStrategy[Community]:
    """Generate a Community."""
    if isinstance(string, AbstractSequence):
        string = st.one_of([st.just(s) for s in string])
    return st.builds(
        Community,
        version,
        string
    )


def hosts(
        host_id: SearchStrategy[int] = uint64s(),
        hostname: Union[SearchStrategy[Text], Sequence[Text]] = st.text(),
        community_list: SearchStrategy[Sequence[Community]] = st.lists(
            communities(), min_size=1, max_size=10
        ),
        parameters: SearchStrategy[Optional[Sequence[ObjectIdentityParameter]]] = (
            optionals(st.lists(object_identity_parameters()))
        ),
        config: Union[SearchStrategy[Optional[Config]], Optional[Config]] = optionals(configs())
) -> SearchStrategy[Host]:
    """Generate a Host."""
    if isinstance(hostname, AbstractSequence):
        hostname = st.one_of([st.just(h) for h in hostname])
    if config is None:
        config = st.none()
    if isinstance(config, Config):
        config = st.just(config)
    return st.builds(
        Host,
        host_id,
        hostname,
        community_list,
        parameters,
        config
    )


def snmp_error_types(
        types: Optional[Sequence[SnmpErrorType]] = None
) -> SearchStrategy[SnmpErrorType]:
    """Generate an SnmpErrorType."""
    if types is None:
        _types = [
            st.just(SnmpErrorType.SESSION_ERROR),
            st.just(SnmpErrorType.CREATE_REQUEST_PDU_ERROR),
            st.just(SnmpErrorType.SEND_ERROR),
            st.just(SnmpErrorType.BAD_RESPONSE_PDU_ERROR),
            st.just(SnmpErrorType.TIMEOUT_ERROR),
            st.just(SnmpErrorType.ASYNC_PROBE_ERROR),
            st.just(SnmpErrorType.TRANSPORT_DISCONNECT_ERROR),
            st.just(SnmpErrorType.CREATE_RESPONSE_PDU_ERROR),
            st.just(SnmpErrorType.VALUE_WARNING),
        ]
    else:
        _types = [st.just(t) for t in types]
    return st.one_of(_types)


def snmp_errors(
        host: SearchStrategy[Host] = hosts(),
        error_type: SearchStrategy[SnmpErrorType] = snmp_error_types(),
        sys_errno: SearchStrategy[Optional[int]] = optionals(int64s()),
        snmp_errno: SearchStrategy[Optional[int]] = optionals(int64s()),
        err_stat: SearchStrategy[Optional[int]] = optionals(int64s()),
        err_index: SearchStrategy[Optional[int]] = optionals(int64s()),
        err_oid: SearchStrategy[Optional[ObjectIdentity]] = optionals(oids()),
        message: SearchStrategy[Optional[Text]] = optionals(st.text())
) -> SearchStrategy[Host]:
    # pylint: disable=too-many-arguments
    """Generate an SnmpError."""
    return st.builds(
        SnmpError,
        error_type,
        host,
        sys_errno,
        snmp_errno,
        err_stat,
        err_index,
        err_oid,
        message
    )


########################
#
#
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
