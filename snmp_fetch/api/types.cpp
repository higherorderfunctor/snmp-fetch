/**
 *  type.cpp - Common type definitions.
 */

#include <optional>

#include "types.hpp"
#include "utils.hpp"

namespace netframe::api {

/**
 *  NullVarBind::operator==
 */
bool NullVarBind::operator==(const NullVarBind &other) {
  return (
      (this->oid == other.oid) &
      (this->oid_size == other.oid_size) &
      (this->value_size == other.value_size)
  );
}


/**
 *  NullVarBind::to_string
 */
std::string NullVarBind::to_string() {
  return str(
      boost::format(
        "NullVarBind("
        "oid=%1%, "
        "oid_size=%2%, "
        "value_size=%3%)"
      )
      % oid_to_string(this->oid)
      % this->oid_size
      % this->value_size
  );
}


/**
 *  SnmpConfig::operator==
 */
bool SnmpConfig::operator==(const SnmpConfig &other) {
  return (
      (this->retries == other.retries) &
      (this->timeout == other.timeout) &
      (this->max_var_binds_per_pdu == other.max_var_binds_per_pdu) &
      (this->max_bulk_repetitions == other.max_bulk_repetitions)
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
        "max_var_binds_per_pdu=%3%, "
        "max_bulk_repetitions=%4%)"
      )
      % this->retries
      % this->timeout
      % this->max_var_binds_per_pdu
      % this->max_bulk_repetitions
  );
}


/**
 *  ObjectIdentityParameter::operator==
 */
bool ObjectIdentityParameter::operator==(const ObjectIdentityParameter &other) {
  return (
      (this->start == other.start) &
      (this->end == other.end)
  );
}


/**
 *  ObjectIdentityParameter::to_string
 */
std::string ObjectIdentityParameter::to_string() {
  return str(
      boost::format(
        "ObjectIdentityParameter("
        "start=%1%, "
        "end=%2%)"
      )
      % oid_to_string(this->start)
      % (this->end.has_value() ? oid_to_string(*this->end) : "None")
  );
}


/**
 *  Host::operator==
 */
bool Host::operator==(const Host &other) {
  return (
      (this->index == other.index) &
      (this->communities == other.communities) &
      //(this->parameters == other.parameters) &
      (this->config == other.config)
  );
}


/**
 *  Host::to_string
 */
std::string Host::to_string() {
  return str(
      boost::format(
        "Host("
        "index=%1%, "
        "communities=%2%, "
        "parameters=%3%, "
        "config=%4%)"
      )
      % this->index
      % "TODO"//% this->communities
      % "TODO"//% (this->parameters.has_value() ? (*this->parameters).to_string() : "None")
      % (this->config.has_value() ? (*this->config).to_string() : "None")
  );
}


/**
 *  SnmpError::operator==
 */
bool SnmpError::operator==(const SnmpError &other) {
  return (
      (this->type == other.type) &
      //(this->host == other.host) &
      (this->sys_errno == other.sys_errno) &
      (this->snmp_errno == other.snmp_errno) &
      (this->err_stat == other.err_stat) &
      (this->err_index == other.err_index) &
      (this->err_oid == other.err_oid) &
      (this->message == other.message)
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
        "host=%2%, "
        "sys_errno=%3%, "
        "snmp_errno=%4%, "
        "err_stat=%5%, "
        "err_index=%6%, "
        "err_oid=%7%, "
        "message=%8%)"
      )
      % type_string
      % this->host.to_string()
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
