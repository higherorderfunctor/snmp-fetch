/**
 *  asyncio.hpp - Async IO handlers.
 */

#ifndef NETFRAME__API__ASYNCIO_HPP
#define NETFRAME__API__ASYNCIO_HPP

#include "results.hpp"
#include "session.hpp"

namespace netframe::api {

/**
 *  async_sessions_send - Dispatch request PDUs.
 *
 *  @param sessions Reference to a list of state wrapped net-snmp sessions.  This function sends
 *                  a request PDU to each.
 *  @param callback Pointer to a callback function once the async request is completed.
 */
void async_sessions_send(
    std::list<async_state> &sessions,
    netsnmp_callback cb
);


/**
 *  async_sessions_read - Read all sockets for response PDUs.
 *
 *  @param sessions Reference to a list of state wrapped net-snmp sessions.  This function checks
 *  each for response PDUs which triggers the callback function on the session.
 */
void async_sessions_read(
    std::list<async_state> &sessions
);


/*
 *  run - Run the main event loop.
 *
 *  @param pdu_type  PDU type of this request.
 *  @param hosts     Reference to the hosts for collection.
 *  @param var_binds Reference to the variable for collection.
 *  @param results   Reference to the results collected.
 *  @param errors    Reference to the errors collected.
 */
void
run(
    int pdu_type,
    std::vector<host_t> &hosts,
    std::vector<var_bind_t> &var_binds,
    std::vector<std::vector<uint8_t>> &results,
    std::vector<SnmpError> &errors,
    SnmpConfig &config
);

}

#endif
