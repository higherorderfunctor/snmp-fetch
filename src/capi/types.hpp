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
#define SNMP_FETCH__DEFAULT_RETRIES 3
#define SNMP_FETCH__DEFAULT_TIMEOUT 3
#define SNMP_FETCH__DEFAULT_MAX_ACTIVE_SESSIONS 10
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
    BULKGET_REQUEST = SNMP_MSG_GETBULK,
};


/**
 *  SnmpConfig - Pure C++ config type exposed through the to python module.
 */
struct SnmpConfig {

  ssize_t retries;
  ssize_t timeout;
  size_t max_active_sessions;
  size_t max_var_binds_per_pdu;
  size_t max_bulk_repetitions;

  /**
   *  SnmpConfig - Constructor with default values.
   */
  SnmpConfig(
      ssize_t retries = SNMP_FETCH__DEFAULT_RETRIES,
      ssize_t timeout = SNMP_FETCH__DEFAULT_TIMEOUT,
      size_t max_active_sessions = SNMP_FETCH__DEFAULT_MAX_ACTIVE_SESSIONS,
      size_t max_var_binds_per_pdu = SNMP_FETCH__DEFAULT_MAX_VAR_BINDS_PER_PDU,
      size_t max_bulk_repetitions = SNMP_FETCH__DEFAULT_MAX_BULK_REPETITIONS
  );

  /**
   *  SnmpConfig::operator==
   */
  bool operator==(const SnmpConfig &a);

  /**
   *  to_string - String method used for __str__ and __repr__ which mimics attrs.
   *
   *  @return String representation of a SnmpConfig.
   */
  std::string to_string();

};


/**
 *  ERROR_TYPE - Constants exposed to python for identifying where an error happened.
 */
enum SNMP_ERROR_TYPE {
    SESSION_ERROR = 0,
    CREATE_REQUEST_PDU_ERROR,
    SEND_ERROR,
    BAD_RESPONSE_PDU_ERROR,
    TIMEOUT_ERROR,
    ASYNC_PROBE_ERROR,
    TRANSPORT_DISCONNECT_ERROR,
    CREATE_RESPONSE_PDU_ERROR,
    VALUE_WARNING
};


/**
 *  SnmpError - Pure C++ container for various error types exposed to python.
 */
struct SnmpError {

  SNMP_ERROR_TYPE type;
  host_t host;
  std::optional<int64_t> sys_errno;
  std::optional<int64_t> snmp_errno;
  std::optional<int64_t> err_stat;
  std::optional<int64_t> err_index;
  std::optional<oid_t> err_oid;
  std::optional<std::string> message;

  /**
   *  SnmpError - Constructor method with default values.
   */
  SnmpError(
    SNMP_ERROR_TYPE type,
    host_t host,
    std::optional<int64_t> sys_errno = {},
    std::optional<int64_t> snmp_errno = {},
    std::optional<int64_t> err_stat = {},
    std::optional<int64_t> err_index = {},
    std::optional<oid_t> err_oid = {},
    std::optional<std::string> message = {}
  );

  /**
   *  SnmpError::operator==
   */
  bool operator==(const SnmpError &a);

  /**
   *  to_string - String method used for __str__ and __repr__ which mimics attrs.
   *
   *  @return String representation of an SnmpError.
   */
  std::string to_string();

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
  SnmpConfig *config;
};

}

#endif
