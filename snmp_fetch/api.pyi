"""Stub file for C++ API."""

from typing import Optional, Sequence, Text, Tuple

import numpy as np

from .types import ObjectIdentity


class NullVarBind:
    # pylint: disable=too-few-public-methods
    """Representation of any empty variable binding."""

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

# /**
#  * ObjectIdentity and buffer sizes for an empty variable binding.
#  *
#  * Buffer sizes are in bytes and padded to 64bits.
#  */
# struct NullVarBind {
#   ObjectIdentity oid;
#   uint64_t oid_size;  // in bytes
#   uint64_t value_size;  // in bytes
#   
#   /**
#    * Convert a NullVarBind to a string.
#    *
#    * @return String representation of a NullVarBind.
#    */
#   std::string to_string();
# 
# };
# 
# 
# /**
#  * Compare two NullVarBinds by value.
#  *
#  * @param lhs Left hand-side NullVarBind to compare.
#  * @param rhs Right hand-side NullVarBind to compare.
#  * @return    Boolean indicating if the left-hand side NullVarBind equals the right-hand side
#  *            NullVarBind.
#  */
# inline bool
# operator==(const NullVarBind& lhs, const NullVarBind &rhs) {
#   return (
#       (lhs.oid == rhs.oid) &
#       (lhs.oid_size == rhs.oid_size) &
#       (lhs.value_size == rhs.value_size)
#   );
# }
# 
# 
# /**
#  * SNMP configuration definition.
#  */
# struct SnmpConfig {
# 
#   ssize_t retries;
#   ssize_t timeout;
#   size_t var_binds_per_pdu;
#   size_t bulk_repetitions;
# 
#   /**
#    * Convert an SnmpConfig to a string.
#    *
#    * @return String representation of an SnmpConfig.
#    */
#   std::string to_string();
# 
# };
# 
# 
# /**
#  * Compare two SnmpConfigs by value.
#  *
#  * @param lhs Left hand-side SnmpConfig to compare.
#  * @param rhs Right hand-side SnmpConfig to compare.
#  * @return    Boolean indicating if the left-hand side SnmpConfig equals the right-hand side
#  *            SnmpConfig.
#  */
# inline bool
# operator==(const SnmpConfig& lhs, const SnmpConfig &rhs) {
#   return (
#       (lhs.retries == rhs.retries) &
#       (lhs.timeout == rhs.timeout) &
#       (lhs.var_binds_per_pdu == rhs.var_binds_per_pdu) &
#       (lhs.bulk_repetitions == rhs.bulk_repetitions)
#   );
# }
# 
# 
# /**
#  * Start and optional end ObjectIdentity parameter.
#  */
# struct ObjectIdentityParameter {
# 
#   ObjectIdentity start;
#   std::optional<ObjectIdentity> end;
# 
#   /**
#    * Convert an ObjectIdentityParameter to a string.
#    *
#    * @return String representation of an ObjectIdentityParameter.
#    */
#   std::string to_string();
# 
# };
# 
# 
# /**
#  * Compare two ObjectIdentityParameters by value.
#  *
#  * @param lhs Left hand-side ObjectIdentityParameter to compare.
#  * @param rhs Right hand-side ObjectIdentityParameter to compare.
#  * @return    Boolean indicating if the left-hand side ObjectIdentityParameter equals the
#  *            right-hand side ObjectIdentityParameter.
#  */
# inline bool
# operator==(const ObjectIdentityParameter& lhs, const ObjectIdentityParameter &rhs) {
#   return (
#       (lhs.start == rhs.start) &
#       (lhs.end == rhs.end)
#   );
# }
# 
# 
# /**
#  * SNMP versions
#  */
# enum SnmpVersion {
#     V2C = 1
# };
# 
# 
# struct SnmpCommunity {
# 
#   uint64_t index;
#   SnmpVersion version;
#   std::string string;
# 
#   /**
#    * Convert an SnmpCommunity to a string.
#    *
#    * @return String representation of an SnmpCommunity.
#    */
#   std::string to_string();
# 
# };
# 
# 
# /**
#  * Compare two SnmpCommunities by value.
#  *
#  * @param lhs Left hand-side SnmpCommunity to compare.
#  * @param rhs Right hand-side SnmpCommunity to compare.
#  * @return    Boolean indicating if the left-hand side SnmpCommunity equals the right-hand side
#  *            SnmpCommunity.
#  */
# inline bool
# operator==(const SnmpCommunity& lhs, const SnmpCommunity &rhs) {
#   return (
#       (lhs.version == rhs.version) &
#       (lhs.string == rhs.string)
#   );
# }
# 
# 
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
#  * Compare two Hosts by value.
#  *
#  * @param lhs Left hand-side Host to compare.
#  * @param rhs Right hand-side Host to compare.
#  * @return    Boolean indicating if the left-hand side Host equals the right-hand side Host.
#  */
# inline bool
# operator==(const Host& lhs, const Host &rhs) {
#   return (
#       (lhs.hostname == rhs.hostname) &
#       (lhs.communities == rhs.communities) &
#       (lhs.parameters == rhs.parameters) &
#       (lhs.config == rhs.config)
#   );
# }
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
# /**
#  * Compare two SnmpErrors by value.
#  *
#  * @param lhs Left hand-side SnmpError to compare.
#  * @param rhs Right hand-side SnmpError to compare.
#  * @return    Boolean indicating if the left-hand side SnmpError equals the right-hand side
#  *            SnmpError.
#  */
# inline bool
# operator==(const SnmpError& lhs, const SnmpError &rhs) {
#   return (
#       (lhs.type == rhs.type) &
#       (lhs.host == rhs.host) &
#       (lhs.sys_errno == rhs.sys_errno) &
#       (lhs.snmp_errno == rhs.snmp_errno) &
#       (lhs.err_stat == rhs.err_stat) &
#       (lhs.err_index == rhs.err_index) &
#       (lhs.err_oid == rhs.err_oid) &
#       (lhs.message == rhs.message)
#   );
# }
# 
# 
# /**
#  * Different statuses of an asynchronous session.
#  */
# enum AsyncStatus {
#   ASYNC_IDLE = 0,
#   ASYNC_WAITING,
#   ASYNC_RETRY
# };
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
# /**
#  * State wrapper for net-snmp callback functions.
#  */
# struct AsyncState {
#   AsyncStatus async_status;
#   void *session;
#   PduType pdu_type;
#   Host host;
#   std::vector<NullVarBind> *var_binds;
#   std::vector<std::vector<NullVarBind>> next_var_binds;
#   std::vector<std::vector<uint8_t>> *results;
#   std::vector<SnmpError> *errors;
#   std::optional<SnmpConfig> config;
# };
# 
# }
# 
# #endif

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


class PduType(type):
    """PduType stub."""

    GET: 'PduType'
    NEXT: 'PduType'
    BULKGET: 'PduType'


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
