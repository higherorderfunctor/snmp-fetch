/**
 *  session.hpp - Session management.
 */

#ifndef SNMP_FETCH__CAPI_HPP
#define SNMP_FETCH__CAPI_HPP

#include <list>

#include "types.hpp"

extern "C" {
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
}

namespace snmp_fetch {

/**
 *  create_netsnmp_session - Create a net-snmp session using the single session API for async
 *  requests.
 *
 *  @param host    Reference to the host for collection.
 *  @param errors  Reference to the errors collected.
 *  @param config  Reference to the configuration.
 *
 *  @return        Returns a void* to the net-snmp session object or NULL on failure.
 */
void *
create_netsnmp_session(
    host_t &host,
    std::vector<SnmpError> &errors,
    SnmpConfig &config
);


/**
 *  create_session - Create a state wrapped net-snmp sessions for callbacks.
 *
 *  @param pdu_type  PDU type of this request.
 *  @param host      Reference to the host for collection.
 *  @param var_binds Reference to the variable bindings for collection.
 *  @param results   Reference to the results collected.
 *  @param errors    Reference to the errors collected.
 *  @param config    Reference to the configuration.
 *  @param sessions  Reference to a list of state wrapped net-snmp sessions.  This function
 *                   appends to this list.
 */
void create_session(
    int pdu_type,
    host_t &host,
    std::vector<var_bind_t> &var_binds,
    std::vector<std::vector<uint8_t>> &results,
    std::vector<SnmpError> &errors,
    SnmpConfig &config,
    std::list<async_state> &sessions
);


/**
 *  close_completed_sessions - Close completed sessions with no remaining work.  Remaining work is
 *  is defined by the contents of next_var_binds.  Recall next_var_binds is a vector of vectors
 *  of var_binds.  The root vector is the partitions based off config.max_var_binds_per_pdu.  The
 *  next vector is the var_binds in that partition.  The size of each partition must not change,
 *  even if work is completed.  The modulus of the request var_binds is used for locating a vector
 *  in next_var_binds when processing results.  To indicate there is no more work, the var_bind
 *  in next_var_bind (also a vector), should be emptied.  When all var_binds in the partition are
 *  empty, it is safe to remove the partition.  A session can be closed when there are no remaining
 *  partition.
 *
 *  @param sessions Reference to a list of state wrapped net-snmp sessions.  This function removes
 *                  completed sessions from this list.
 */
void close_completed_sessions(
    std::list<async_state> &sessions
);

}

#endif
