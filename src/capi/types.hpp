/**
 *  type.hpp - Common type definitions.
 */

#ifndef SNMP_FETCH__TYPES_H
#define SNMP_FETCH__TYPES_H

#include <iostream>
#include <boost/format.hpp>

extern "C" {
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
}

#include "utils.hpp"

namespace snmp_fetch {

// default values
#define SNMP_FETCH__DEFAULT_RETRIES 2
#define SNMP_FETCH__DEFAULT_TIMEOUT 2
#define SNMP_FETCH__DEFAULT_MAX_ACTIVE_SESSIONS 8
#define SNMP_FETCH__DEFAULT_MAX_VAR_BINDS_PER_PDU 10
#define SNMP_FETCH__DEFAULT_MAX_BULK_REPETITIONS 10


// type aliases
using host_t = std::tuple<uint64_t, std::string, std::string>;
using oid_t = std::vector<uint64_t>;
using oid_size_t = uint64_t;
using value_size_t = uint64_t;
using var_bind_size_t = std::tuple<oid_size_t, value_size_t>;
using var_bind_t = std::tuple<oid_t, var_bind_size_t>;


/**
 *  async_status_t - Different statuses of an async session.
 */
enum async_status_t {
  ASYNC_IDLE = 0,
  ASYNC_WAITING,
  ASYNC_RETRY
};


/**
 *  PDU_TYPE - Constants exposed to python.
 */
enum PDU_TYPE {
    GET_REQUEST = SNMP_MSG_GET,
    NEXT_REQUEST = SNMP_MSG_GETNEXT,
    GETBULK_REQUEST = SNMP_MSG_GETBULK,
};


/**
 *  Config - Pure C++ config type exposed through the to python module.
 */
struct Config {
  ssize_t retries;
  ssize_t timeout;
  size_t max_active_sessions;
  size_t max_var_binds_per_pdu;
  size_t max_bulk_repetitions;

  /**
   *  Config - Constructor with default values.
   */
  Config(
      ssize_t retries = SNMP_FETCH__DEFAULT_RETRIES,
      ssize_t timeout = SNMP_FETCH__DEFAULT_TIMEOUT,
      size_t max_active_sessions = SNMP_FETCH__DEFAULT_MAX_ACTIVE_SESSIONS,
      size_t max_var_binds_per_pdu = SNMP_FETCH__DEFAULT_MAX_VAR_BINDS_PER_PDU,
      size_t max_bulk_repetitions = SNMP_FETCH__DEFAULT_MAX_BULK_REPETITIONS
  ) {
    this->retries = retries;
    this->timeout = timeout;
    this->max_active_sessions = max_active_sessions;
    this->max_var_binds_per_pdu = max_var_binds_per_pdu;
    this->max_bulk_repetitions = max_bulk_repetitions;
  }

  /**
   *  to_string - String method used for __str__ and __repr__ which mimics attrs.
   *
   *  @return String representation of a Config.
   */
  std::string to_string() {
    return str(
        boost::format(
          "Config("
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
};


/**
 *  ERROR_TYPE - Constants exposed to python for identifying where an error happened.
 */
enum ERROR_TYPE {
    SESSION_ERROR = 0,
    CREATE_REQUEST_PDU_ERROR,
    SEND_ERROR,
    BAD_RESPONSE_PDU_ERROR,
    TIMEOUT_ERROR,
    ASYNC_PROBE_ERROR,
    TRANSPORT_DISCONNECT_ERROR,
    CREATE_RESPONSE_PDU_ERROR,
};


/**
 *  SnmpError - Pure C++ container for various error types exposed to python.
 */
struct SnmpError {
  ERROR_TYPE type;
  host_t host;
  std::optional<int64_t> sys_errno;
  std::optional<int64_t> snmp_errno;
  std::optional<int64_t> errstat;
  std::optional<int64_t> errindex;
  std::optional<oid_t> erroid;
  std::optional<std::string> message;

  /**
   *  SnmpError - Constructor method with default values.
   */
  SnmpError(
    ERROR_TYPE type,
    host_t host,
    std::optional<int64_t> sys_errno = {},
    std::optional<int64_t> snmp_errno = {},
    std::optional<int64_t> errstat = {},
    std::optional<int64_t> errindex = {},
    std::optional<oid_t> erroid = {},
    std::optional<std::string> message = {}
  ) {
    this->type = type;
    this->host = std::make_tuple(
        std::get<0>(host),
        std::get<1>(host),
        std::get<2>(host)
    );
    this->sys_errno = sys_errno;
    this->snmp_errno = snmp_errno;
    this->errstat = errstat;
    this->errindex = errindex;
    this->erroid = erroid;
    this->message = message;
  }

  /**
   *  to_string - String method used for __str__ and __repr__ which mimics attrs.
   *
   *  @return String representation of an SnmpError.
   */
  std::string to_string() {
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
    };

    std::string repr = str(
        boost::format(
          "SnmpError("
          "type=%1%, "
          "Host(index=%2%, hostname='%3%', community='%4%'), "
          "sys_errno=%5%, "
          "snmp_errno=%6%, "
          "errstat=%7%, "
          "errindex=%8%, "
          "var_bind=%9%, "
          "message=%10%"
          ")"//, loc
        )
        % type_string
        % std::to_string(std::get<0>(this->host))
        % std::get<1>(this->host)
        % std::get<2>(this->host)
        % (this->sys_errno.has_value() ? std::to_string(*this->sys_errno) : "None")
        % (this->snmp_errno.has_value() ? std::to_string(*this->snmp_errno) : "None")
        % (this->errstat.has_value() ? std::to_string(*this->errstat) : "None")
        % (this->errindex.has_value() ? std::to_string(*this->errindex) : "None")
        % (
          this->erroid.has_value() ? "'" + oid_to_string(
            (*this->erroid).data(),
            (*this->erroid).size()
          ) + "'" : "None"
        )
        % ("'" + this->message.has_value() ? *this->message + "'" : "None")
    );
    // std::cerr << repr << std::endl;
    return repr;
  }
};


/**
 *  async_state - State wrapper for net-snmp sessions.
 *
 *  Host should be left as copy as the underlying pending host list destroys the elements that
 *  were used to build this structure.
 */
struct async_state {
  async_status_t async_status;
  void *session;
  int pdu_type;
  host_t host;
  std::vector<var_bind_t> *var_binds;
  std::vector<std::vector<oid_t>> next_var_binds;
  std::vector<std::vector<uint8_t>> *results;
  std::vector<SnmpError> *errors;
  Config *config;
};

}

#endif
