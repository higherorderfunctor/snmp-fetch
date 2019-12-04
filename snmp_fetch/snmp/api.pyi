# pylint: disable=missing-class-docstring, too-few-public-methods, unused-argument, no-self-use
# pylint: disable=too-many-arguments, redefined-builtin, missing-function-docstring
"""netframe::snmp::api C++ extension stub."""

from typing import List, Optional, Sequence, Text, Tuple

import numpy as np

from .types import ObjectIdentity


class PduType(type):  # noqa: D101
    GET: 'PduType'
    NEXT: 'PduType'
    BULKGET: 'PduType'


class NullVarBind:  # noqa: D101

    oid: ObjectIdentity
    oid_size: int
    value_size: int

    def __init__(  # noqa: D107
        self,
        oid: ObjectIdentity,
        oid_size: int,
        value_size: int
    ) -> None: ...


class Config:  # noqa: D101

    retries: int
    timeout: int
    var_binds_per_pdu: int
    bulk_repetitions: int

    def __init__(  # noqa: D107
        self,
        retries: int = ...,
        timeout: int = ...,
        var_binds_per_pdu: int = ...,
        bulk_repetitions: int = ...
    ) -> None: ...


class ObjectIdentityParameter:  # noqa: D101

    start: Optional[ObjectIdentity]
    end: Optional[ObjectIdentity]

    def __init__(  # noqa: D107
        self,
        start: ObjectIdentity = ...,
        end: Optional[ObjectIdentity] = ...,
    ) -> None: ...


class Version(type):  # noqa: D101
    V2C: 'Version'


class Community:  # noqa: D101

    version: Version
    string: Text

    def __init__(  # noqa: D107
        self,
        version: Version,
        string: Text
    ) -> None: ...


class Host:  # noqa: D101

    id: int
    hostname: Text
    communities: List[Community]
    parameters: Optional[List[ObjectIdentityParameter]]
    config: Optional[Config]

    def __init__(  # noqa: D107
        self,
        index: int,
        hostname: Text,
        communities: List[Community],
        parameters: Optional[List[ObjectIdentityParameter]] = ...,
        config: Optional[Config] = ...
    ) -> None: ...

    def snapshot(  # noqa: D102
        self
    ) -> 'Host': ...


class SnmpErrorType(type):  # noqa: D101
    SESSION_ERROR: 'SnmpErrorType'
    CREATE_REQUEST_PDU_ERROR: 'SnmpErrorType'
    SEND_ERROR: 'SnmpErrorType'
    BAD_RESPONSE_PDU_ERROR: 'SnmpErrorType'
    TIMEOUT_ERROR: 'SnmpErrorType'
    ASYNC_PROBE_ERROR: 'SnmpErrorType'
    TRANSPORT_DISCONNECT_ERROR: 'SnmpErrorType'
    CREATE_RESPONSE_PDU_ERROR: 'SnmpErrorType'
    VALUE_WARNING: 'SnmpErrorType'


class SnmpError:  # noqa: D101

    type: SnmpErrorType
    host: Host
    sys_errno: Optional[int]
    snmp_errno: Optional[int]
    err_stat: Optional[int]
    err_index: Optional[int]
    err_oid: Optional[Sequence[int]]
    message: Optional[Text]

    def __init__(  # noqa: D107
        self,
        type: SnmpErrorType,
        host: Host,
        sys_errno: Optional[int] = ...,
        snmp_errno: Optional[int] = ...,
        err_stat: Optional[int] = ...,
        err_index: Optional[int] = ...,
        err_oid: Optional[Sequence[int]] = ...,
        message: Optional[Text] = ...
    ) -> None: ...


def dispatch(  # noqa: D103
    pdu_type: PduType,
    hosts: Sequence[Host],
    null_var_binds: Sequence[NullVarBind],
    config: Optional[Config] = ...,
    max_active_async_sessions: int = ...,
) -> Tuple[Sequence[np.ndarray], Sequence[SnmpError]]: ...
