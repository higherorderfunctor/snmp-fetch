/**
 * Common type implementations.
 */

#include <numeric>

#include "types.hpp"
#include "utils.hpp"

namespace netframe::api {

std::string NullVarBind::to_string() {
  return str(
      boost::format(
        "NullVarBind("
        "oid='%1%', "
        "oid_size=%2%, "
        "value_size=%3%)"
      )
      % oid_to_string(this->oid)
      % this->oid_size
      % this->value_size
  );
}

std::string SnmpConfig::to_string() {
  return str(
      boost::format(
        "SnmpConfig("
        "retries=%1%, "
        "timeout=%2%, "
        "var_binds_per_pdu=%3%, "
        "bulk_repetitions=%4%)"
      )
      % this->retries
      % this->timeout
      % this->var_binds_per_pdu
      % this->bulk_repetitions
  );
}

std::string ObjectIdentityParameter::to_string() {
  return str(
      boost::format(
        "ObjectIdentityParameter("
        "start='%1%', "
        "end=%2%)"
      )
      % oid_to_string(this->start)
      % (this->end.has_value() ? "'"+oid_to_string(*this->end)+"'" : "None")
  );
}

std::string SnmpCommunity::to_string() {
  std::string version_string = "UNKNOWN_VERSION";
  switch (this->version) {
    case V2C:
      version_string = "V2C";
      break;
  };

  return str(
      boost::format(
        "SnmpCommunity("
        "index=%1%, "
        "version=%2%, "
        "string=%3%)"
      )
      % this->index
      % version_string
      % this->string
  );
}

std::string Host::to_string() {
  std::optional<std::list<std::string>> communities = {};
  if (!this->communities.empty()) {
    communities = std::list<std::string>();
    std::transform(
      this->communities.begin(), this->communities.end(), std::back_inserter(*communities),
      [](auto&& community) -> std::string { return community.to_string(); }
    );
  }
  std::optional<std::list<std::string>> parameters = {};
  if (this->parameters.has_value() && !this->parameters->empty()) {
    parameters = std::list<std::string>();
    std::transform(
      this->parameters->begin(), this->parameters->end(), std::back_inserter(*parameters),
      [](auto&& parameter) -> std::string { return parameter.to_string(); }
    );
  }
  return str(
      boost::format(
        "Host("
        "index=%1%, "
        "hostname='%2%', " 
        "communities=%3%, "
        "parameters=%4%, "
        "config=%5%)"
      )
      % this->index
      % this->hostname
      % (
        communities.has_value()
        ? (
          "[" + std::accumulate(
          next(communities->begin()), communities->end(), communities->front(),
            [](auto&& lhs, auto&& rhs) -> std::string { return lhs + ", " + rhs; }
          ) + "]"
        )
        : "[]"
      )
      % (
        parameters.has_value()
        ? (
          "[" + std::accumulate(
          next(parameters->begin()), parameters->end(), parameters->front(),
            [](auto&& lhs, auto&& rhs) -> std::string { return lhs + ", " + rhs; }
          ) + "]"
        )
        : "None"
      )
      % (this->config.has_value() ? (*this->config).to_string() : "None")
  );
}

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
      % (this->err_oid.has_value() ? "'" + oid_to_string(*this->err_oid) + "'" : "None")
      % (this->message.has_value() ? "'" + *this->message + "'" : "None")
  );
}

}
