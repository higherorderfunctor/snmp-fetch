/**
 * Session management definitions.
 */

#ifndef NETFRAME__SNMP__API__SESSION_HPP
#define NETFRAME__SNMP__API__SESSION_HPP

#include "types.hpp"

namespace netframe::snmp::api {

/**
 * Create a net-snmp session using the single session API for async requests.
 *
 * @param host    Reference to the host for collection.
 * @param errors  Reference to the errors collected.
 * @param config  Reference to the configuration.
 *
 * @return        Returns a void* to the net-snmp session object or NULL on failure.
 */
void *
create_netsnmp_session(
    Host& host,
    std::vector<SnmpError>& errors,
    std::optional<Config>& config
);


/**
 * Create a state wrapped net-snmp sessions for callbacks.
 *
 * @param pdu_type  PDU type of this request.
 * @param host      Reference to the host for collection.
 * @param var_binds Reference to the variable bindings for collection.
 * @param results   Reference to the results collected.
 * @param errors    Reference to the errors collected.
 * @param config    Reference to the configuration.
 * @param sessions  Reference to a list of state wrapped net-snmp sessions.  This function
 *                  appends to this list.
 */
void create_session(
    PduType pdu_type,
    Host& host,
    std::vector<NullVarBind>& null_var_binds,
    std::vector<std::vector<uint8_t>>& results,
    std::vector<SnmpError>& errors,
    std::optional<Config>& config,
    std::list<AsyncSession>& sessions
);


/**
 * Close completed sessions with no remaining work.  Remaining work is defined by the contents of
 * next_var_binds.  Recall next_var_binds is a vector of vectors of NullVarBinds.  The root vector
 * is the partitions based off config.max_var_binds_per_pdu.  The next vector is the NullVarBind in
 * that partition.  The size of each partition must not change, even if work is completed.  The
 * modulus of the request NullVarBind is used for locating a vector in next_var_binds when processing
 * results.  To indicate there is no more work, the NullVarBind in next_var_bind (also a vector),
 * should be emptied.  When all NullVarBinds in the partition are empty, the partition should be removed.
 * A session can be closed when there are no remaining partition.
 *
 * @param sessions Reference to a list of state wrapped net-snmp sessions.  This function removes
 *                 completed sessions from this list.
 */
void close_completed_sessions(
    std::list<AsyncSession>& sessions
);

}

#endif
