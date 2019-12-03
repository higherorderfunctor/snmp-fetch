/**
 *  Async function definitions.
 */

#ifndef NETFRAME__SNMP__API__ASYNCIO_HPP
#define NETFRAME__SNMP__API__ASYNCIO_HPP

#include "results.hpp"

namespace netframe::snmp::api {

/**
 * Dispatch request PDUs to a list of sessions.
 *
 * @param sessions Reference to a list of AsyncSessions.
 * @param callback Pointer to a callback function once the async request is completed.
 */
void async_sessions_send(
    std::list<AsyncSession>& sessions,
    netsnmp_callback cb
);


/**
 * Read all sockets for response PDUs and call the callback for each.
 *
 * @param sessions Reference to a list of AsyncSessions.
 */
void async_sessions_read(
    std::list<AsyncSession>& sessions
);


/**
 * Run the main event loop.
 *
 * @param pdu_type              PDU type of this request.
 * @param hosts                 Reference to the hosts for collection.
 * @param var_binds             Reference to the variable for collection.
 * @param results               Reference to the results collected.
 * @param errors                Reference to the errors collected.
 * @param config                Optional default SNMP config.
 * @param max_active_sessions   Maximum number of active async sessions.
 */
void
run(
    PduType pdu_type,
    std::list<Host> hosts,
    std::vector<NullVarBind>& null_var_binds,
    std::vector<std::vector<uint8_t>>& results,
    std::vector<SnmpError>& errors,
    std::optional<Config>& config,
    uint64_t max_active_async_sessions
);

}

#endif
