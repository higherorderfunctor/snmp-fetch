/**
 *  type.cpp - Common type definitions.
 */

#include "types.hpp"

namespace snmp_fetch {

/**
 *  SnmpConfig::SnmpConfig
 */
SnmpConfig::SnmpConfig(
      ssize_t retries,
      ssize_t timeout,
      size_t max_active_sessions,
      size_t max_var_binds_per_pdu,
      size_t max_bulk_repetitions
  ) {
    this->retries = retries;
    this->timeout = timeout;
    this->max_active_sessions = max_active_sessions;
    this->max_var_binds_per_pdu = max_var_binds_per_pdu;
    this->max_bulk_repetitions = max_bulk_repetitions;
  }


/**
 *  SnmpConfig::operator==
 */
bool SnmpConfig::operator==(const SnmpConfig &a) {
  return (
      (a.retries == this->retries) &
      (a.timeout == this->timeout) &
      (a.max_active_sessions == this->max_active_sessions) &
      (a.max_var_binds_per_pdu == this->max_var_binds_per_pdu) &
      (a.max_bulk_repetitions == this->max_bulk_repetitions)
  );
}


/**
 *  SnmpConfig::to_string
 */
std::string SnmpConfig::to_string() {
  return str(
      boost::format(
        "SnmpConfig("
        "retries=%1%, "
        "timeout=%2%, "
        "max_active_sessions=%3%, "
        "max_var_binds_per_pdu=%4%, "
        "max_bulk_repetitions=%5%"
        ")"
      )
      % this->retries
      % this->timeout
      % this->max_active_sessions
      % this->max_var_binds_per_pdu
      % this->max_bulk_repetitions
  );
}


/**
 *  SnmpError::SnmpError
 */
SnmpError::SnmpError(
  SNMP_ERROR_TYPE type,
  host_t host,
  std::optional<int64_t> sys_errno,
  std::optional<int64_t> snmp_errno,
  std::optional<int64_t> err_stat,
  std::optional<int64_t> err_index,
  std::optional<oid_t> err_oid,
  std::optional<std::string> message
) {
  this->type = type;
  this->host = std::make_tuple(
      std::get<0>(host),
      std::get<1>(host),
      std::get<2>(host)
  );
  this->sys_errno = sys_errno;
  this->snmp_errno = snmp_errno;
  this->err_stat = err_stat;
  this->err_index = err_index;
  this->err_oid = err_oid;
  this->message = message;
}


/**
 *  SnmpError::operator==
 */
bool SnmpError::operator==(const SnmpError &a) {
  return (
      (a.type == this->type) &
      (a.host == this->host) &
      (a.sys_errno == this->sys_errno) &
      (a.snmp_errno == this->snmp_errno) &
      (a.err_stat == this->err_stat) &
      (a.err_index == this->err_index) &
      (a.err_oid == this->err_oid) &
      (a.message == this->message)
  );
}


/**
  *  SnmpError::to_string
  */
std::string SnmpError::to_string() {
  std::string type_string = "UNKNOWN_ERROR";
  switch (this->type) {
    case SESSION_ERROR:
      type_string = "SESSION_ERROR";
      break;
    case CREATE_REQUEST_PDU_ERROR:
      type_string = "CREATE_REQUEST_PDU_ERROR";
      break;
    case SEND_ERROR:
      type_string = "SEND_ERROR";
      break;
    case BAD_RESPONSE_PDU_ERROR:
      type_string = "BAD_RESPONSE_PDU_ERROR";
      break;
    case TIMEOUT_ERROR:
      type_string = "TIMEOUT_ERROR";
      break;
    case ASYNC_PROBE_ERROR:
      type_string = "ASYNC_PROBE_ERROR";
      break;
    case TRANSPORT_DISCONNECT_ERROR:
      type_string = "TRANSPORT_DISCONNECT_ERROR";
      break;
    case CREATE_RESPONSE_PDU_ERROR:
      type_string = "CREATE_RESPONSE_PDU_ERROR";
      break;
    case VALUE_WARNING:
      type_string = "VALUE_WARNING";
      break;
  };

  return str(
      boost::format(
        "SnmpError("
        "type=%1%, "
        "Host(index=%2%, hostname='%3%', community='%4%'), "
        "sys_errno=%5%, "
        "snmp_errno=%6%, "
        "err_stat=%7%, "
        "err_index=%8%, "
        "err_oid=%9%, "
        "message=%10%"
        ")"
      )
      % type_string
      % std::to_string(std::get<0>(this->host))
      % std::get<1>(this->host)
      % std::get<2>(this->host)
      % (this->sys_errno.has_value() ? std::to_string(*this->sys_errno) : "None")
      % (this->snmp_errno.has_value() ? std::to_string(*this->snmp_errno) : "None")
      % (this->err_stat.has_value() ? std::to_string(*this->err_stat) : "None")
      % (this->err_index.has_value() ? std::to_string(*this->err_index) : "None")
      % (
        this->err_oid.has_value() ? "'" + oid_to_string(
          (*this->err_oid).data(),
          (*this->err_oid).size()
        ) + "'" : "None"
      )
      % (this->message.has_value() ? "'" + *this->message + "'" : "None")
  );
}

}
