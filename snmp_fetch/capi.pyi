"""Stub file for C API."""

from typing import Optional, Sequence, Text, Tuple

import numpy as np


class ErrorType(type):
    """ErrorType stub."""

    SESSION_ERROR: 'ErrorType'
    CREATE_REQUEST_PDU_ERROR: 'ErrorType'
    SEND_ERROR: 'ErrorType'
    BAD_RESPONSE_PDU_ERROR: 'ErrorType'
    TIMEOUT_ERROR: 'ErrorType'
    ASYNC_PROBE_ERROR: 'ErrorType'
    TRANSPORT_DISCONNECT_ERROR: 'ErrorType'
    CREATE_RESPONSE_PDU_ERROR: 'ErrorType'


class SnmpError:
    # pylint: disable=too-few-public-methods
    """SnmpError stub."""

    type: ErrorType
    host: Tuple[int, Text, Text]
    sys_errno: Optional[int]
    snmp_errno: Optional[int]
    err_stat: Optional[int]
    err_index: Optional[int]
    err_oid: Optional[Sequence[int]]
    message: Optional[Text]

    retries: int
    timeout: int
    max_active_sessions: int
    max_var_binds_per_pdu: int
    max_bulk_repetitions: int

    def __init__(
            self,
            type: ErrorType,
            host: Tuple[int, Text, Text],
            sys_errno: Optional[int] = ...,
            snmp_errno: Optional[int] = ...,
            err_stat: Optional[int] = ...,
            err_index: Optional[int] = ...,
            err_oid: Optional[Sequence[int]] = ...,
            message: Optional[Text] = ...
    ) -> None:
        # pylint: disable=too-many-arguments, unused-argument, redefined-builtin
        """Initialize an SNMP config object."""
        ...


class PduType(type):
    """PduType stub."""

    GET_REQUEST: 'PduType'
    NEXT_REQUEST: 'PduType'
    BULKGET_REQUEST: 'PduType'


class SnmpConfig:
    # pylint: disable=too-few-public-methods
    """SnmpConfig stub."""

    retries: int
    timeout: int
    max_active_sessions: int
    max_var_binds_per_pdu: int
    max_bulk_repetitions: int

    def __init__(
            self,
            retries: int = ...,
            timeout: int = ...,
            max_active_sessions: int = ...,
            max_var_binds_per_pdu: int = ...,
            max_bulk_repetitions: int = ...
    ) -> None:
        # pylint: disable=too-many-arguments, unused-argument
        """Initialize an SNMP error object."""
        ...


def fetch(
        pdu_type: PduType,
        hosts: Sequence[Tuple[int, Text, Text]],
        var_binds: Sequence[Tuple[Sequence[int], Tuple[int, int]]],
        config: SnmpConfig = ...
) -> Tuple[Sequence[np.ndarray], Sequence[SnmpError]]:
    # pylint: disable=unused-argument
    """Fetch SNMP objects via the C API."""
    ...
