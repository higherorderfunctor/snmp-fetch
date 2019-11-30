"""netframe::snmp::api C++ extension stub."""

from typing import Optional, Sequence, Text, Tuple

import numpy as np

from .types import ObjectIdentity


class PduType(type):
    """PduType stub."""

    GET: 'PduType'
    NEXT: 'PduType'
    BULKGET: 'PduType'


class NullVarBind:
    # pylint: disable=too-few-public-methods
    """NullVarBind stub."""

    oid: ObjectIdentity
    oid_size: int
    value_size: int

    def __init__(
            self,
            oid: ObjectIdentity,
            oid_size: int,
            value_size: int
    ) -> None:
        # pylint: disable=too-many-arguments, unused-argument, redefined-builtin
        """Initialize a NullVarBind."""
        ...


class Config:
    # pylint: disable=too-few-public-methods
    """Config stub."""

    retries: int
    timeout: int
    var_binds_per_pdu: int
    bulk_repetitions: int

    def __init__(
            self,
            retries: int = ...,
            timeout: int = ...,
            var_binds_per_pdu: int = ...,
            bulk_repetitions: int = ...
    ) -> None:
        # pylint: disable=too-many-arguments, unused-argument
        """Initialize an SNMP error object."""
        ...


class ObjectIdentityParameter:
    # pylint: disable=too-few-public-methods
    """ObjectIdentityParameter stub."""

    start: ObjectIdentity
    end: Optional[ObjectIdentity]

    def __init__(
            self,
            start: ObjectIdentity,
            end: Optional[ObjectIdentity] = ...,
    ) -> None:
        # pylint: disable=too-many-arguments, unused-argument, redefined-builtin
        """Initialize an ObjectIdentityParameter."""
        ...


class Version(type):
    """Version stub."""

    V2C: 'Version'


class Community:
    # pylint: disable=too-few-public-methods
    """Community stub."""

    index: int
    version: Version
    community: Text

    def __init__(
            self,
            index: int,
            version: Version,
            community: Text
    ) -> None:
        # pylint: disable=too-many-arguments, unused-argument, redefined-builtin
        """Initialize an SnmpCommunity."""
        ...

# /**
#  * Host configuration.
#  */
# struct Host {
# 
#   uint64_t index;
#   std::string hostname;
#   std::list<SnmpCommunity> communities;
#   std::optional<std::list<ObjectIdentityParameter>> parameters;
#   std::optional<SnmpConfig> config;
# 
#   /**
#    * Convert a Host to a string.
#    *
#    * @return String representation of a Host.
#    */
#   std::string to_string();
# 
# };
# 
# 
# /**
#  * SNMP error types.
#  */
# enum SnmpErrorType {
#     SESSION_ERROR = 0,
#     CREATE_REQUEST_PDU_ERROR,
#     SEND_ERROR,
#     BAD_RESPONSE_PDU_ERROR,
#     TIMEOUT_ERROR,
#     ASYNC_PROBE_ERROR,
#     TRANSPORT_DISCONNECT_ERROR,
#     CREATE_RESPONSE_PDU_ERROR,
#     VALUE_WARNING
# };
# 
# 
# /**
#  * SNMP error definition.
#  */
# struct SnmpError {
# 
#   SnmpErrorType type;
#   Host host;
#   std::optional<int64_t> sys_errno;
#   std::optional<int64_t> snmp_errno;
#   std::optional<int64_t> err_stat;
#   std::optional<int64_t> err_index;
#   std::optional<ObjectIdentity> err_oid;
#   std::optional<std::string> message;
# 
#   /**
#    * Convert an SnmpError to a string.
#    *
#    * @return String representation of an SnmpError.
#    */
#   std::string to_string();
# 
# };
# 
# 
# 
# /**
#  * SNMP PDU types.
#  */
# enum PduType {
#     GET = SNMP_MSG_GET,
#     NEXT= SNMP_MSG_GETNEXT,
#     BULKGET = SNMP_MSG_GETBULK,
# };
# 
# 

class SnmpErrorType(type):
    """ErrorType stub."""

    SESSION_ERROR: 'SnmpErrorType'
    CREATE_REQUEST_PDU_ERROR: 'SnmpErrorType'
    SEND_ERROR: 'SnmpErrorType'
    BAD_RESPONSE_PDU_ERROR: 'SnmpErrorType'
    TIMEOUT_ERROR: 'SnmpErrorType'
    ASYNC_PROBE_ERROR: 'SnmpErrorType'
    TRANSPORT_DISCONNECT_ERROR: 'SnmpErrorType'
    CREATE_RESPONSE_PDU_ERROR: 'SnmpErrorType'
    VALUE_WARNING: 'SnmpErrorType'


class SnmpError:
    # pylint: disable=too-few-public-methods
    """SnmpError stub."""

    type: SnmpErrorType
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
            type: SnmpErrorType,
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






def fetch(
        pdu_type: PduType,
        hosts: Sequence[Tuple[int, Text, Text]],
        var_binds: Sequence[Tuple[Sequence[int], Tuple[int, int]]],
        config: Config = ...
) -> Tuple[Sequence[np.ndarray], Sequence[SnmpError]]:
    # pylint: disable=unused-argument
    """Fetch SNMP objects via the C API."""
    ...
