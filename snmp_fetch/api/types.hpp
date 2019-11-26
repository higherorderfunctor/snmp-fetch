/**
 *  type.hpp - Common type definitions.
 */

#ifndef NETFRAME__API__TYPES_H
#define NETFRAME__API__TYPES_H

#include <list>
#include <iostream>
#include <boost/format.hpp>

extern "C" {
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
}

#include "utils.hpp"

namespace netframe::api {

// default values
#define DEFAULT_MAX_ACTIVE_SESSIONS 10
#define DEFAULT_RETRIES 3
#define DEFAULT_TIMEOUT 3
#define DEFAULT_MAX_VAR_BINDS_PER_PDU 10
#define DEFAULT_MAX_BULK_REPETITIONS 10


// type aliases
using ObjectIdentity = std::vector<uint64_t>;


/**
 *  AsyncStatus - Different statuses of an asynchronous session.
 */
enum AsyncStatus {
  ASYNC_IDLE = 0,
  ASYNC_WAITING,
  ASYNC_RETRY
};


/**
 *  PduType - SNMP PDU types.
 */
enum PduType {
    GET = SNMP_MSG_GET,
    NEXT= SNMP_MSG_GETNEXT,
    BULKGET = SNMP_MSG_GETBULK,
};


/**
 *  NullVarBind - ObjectIdentity and buffer sizes for a null variable binding to be filled.
 */
struct NullVarBind {
  ObjectIdentity oid;
  uint64_t oid_size;
  uint64_t value_size;

  /**
   *  NullVarBind::operator== - Compare two null variable bindings by value.
   *
   *  @param other The other SnmpConfig to compare.
   *  @return      Boolean indicating if the other NullVarBind equals this one.
   */
  bool operator==(const NullVarBind &other);

  /**
   *  to_string - String method used for __str__ and __repr__ which mimics attrs.
   *
   *  @return String representation of a NullVarBind.
   */
  std::string to_string();

};


/**
 *  SnmpConfig - SNMP configuration.
 */
struct SnmpConfig {

  ssize_t retries;
  ssize_t timeout;
  size_t max_var_binds_per_pdu;
  size_t max_bulk_repetitions;

  /**
   *  SnmpConfig::operator== - Compare two SNMP configurations by value.
   *
   *  @param other The other SnmpConfig to compare.
   *  @return      Boolean indicating if the other SnmpConfig equals this SnmpConfig.
   */
  bool operator==(const SnmpConfig &other);

  /**
   *  to_string - String method used for __str__ and __repr__ which mimics attrs.
   *
   *  @return String representation of a SnmpConfig.
   */
  std::string to_string();

};


/**
 *  ObjectIdentityParameter - Start and optional end ObjectIdentity parameter.
 */
struct ObjectIdentityParameter {

  ObjectIdentity start;
  std::optional<ObjectIdentity> end;

  /**
   *  ObjectIdentityParameter::operator== - Compare two object identity parameters by value.
   *
   *  @param other The other ObjectIdentityParameter to compare.
   *  @return      Boolean indicating if the other Parameter equals this Parameter.
   */
  bool operator==(const ObjectIdentityParameter &other);

  /**
   *  to_string - String method used for __str__ and __repr__ which mimics attrs.
   *
   *  @return String representation of a ObjectIdentityParameter.
   */
  std::string to_string();

};


/**
 *  Host - Host configuration.
 */
struct Host {
  uint64_t index;
  std::string hostname;
  std::list<std::string> communities;
  std::optional<std::list<ObjectIdentityParameter>> parameters;
  std::optional<SnmpConfig> config;

  /**
   *  Host::operator== - Compare two host configurations by value.
   *
   *  @param other The other host to compare.
   *  @return      Boolean indicating if the other host equals this host.
   */
  bool operator==(const Host &other);

  /**
   *  to_string - String method used for __str__ and __repr__ which mimics attrs.
   *
   *  @return String representation of a Host.
   */
  std::string to_string();
};


/**
 *  SnmpErrorType - SNMP error types.
 */
enum SnmpErrorType {
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
 *  SnmpError - SNMP error.
 */
struct SnmpError {

  SnmpErrorType type;
  Host host;
  std::optional<int64_t> sys_errno;
  std::optional<int64_t> snmp_errno;
  std::optional<int64_t> err_stat;
  std::optional<int64_t> err_index;
  std::optional<ObjectIdentity> err_oid;
  std::optional<std::string> message;

  /**
   *  SnmpError::operator== - Compare two SNMP errors by value.
   *
   *  @param other The other SnmpError to compare.
   *  @return      Boolean indicating if the other SnmpError equals this SnmpError.
   */
  bool operator==(const SnmpError &other);

  /**
   *  to_string - String method used for __str__ and __repr__ which mimics attrs.
   *
   *  @return String representation of an SnmpError.
   */
  std::string to_string();

};


/**
 *  AsyncState - State wrapper for net-snmp sessions and callbacks.
 */
struct AsyncState {
  AsyncStatus async_status;
  void *session;
  int pdu_type;
  Host host;
  std::vector<NullVarBind> *var_binds;
  std::vector<std::vector<NullVarBind>> next_var_binds;
  std::vector<std::vector<uint8_t>> *results;
  std::vector<SnmpError> *errors;
  SnmpConfig *config;
};

}

#endif
