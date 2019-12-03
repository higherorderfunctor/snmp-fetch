/**
 *  Async function implementations.
 */

#include "asyncio.hpp"

#include "session.hpp"

namespace netframe::snmp::api {

void async_sessions_send(
    std::list<AsyncSession>& sessions,
    netsnmp_callback cb
) {

    // iterate through each session
    for (auto&& ss: sessions) {
      // skip sessions that are not idle
      if (ss.async_status != ASYNC_IDLE)
        continue;

      // create the request PDU
      netsnmp_pdu *pdu = snmp_pdu_create(ss.pdu_type);

      // log PDU creation failures
      if (!pdu) {
        ss.errors->push_back((SnmpError) {
              CREATE_REQUEST_PDU_ERROR,
              ss.host->snapshot(),
              {},
              {},
              {},
              {},
              {},
              "Failed to allocate memory for the request PDU"
        });
        return;
      }

      // set PDU options based on PDU type
      switch (ss.pdu_type) {
        case BULKGET:
          pdu->non_repeaters = 0;
          pdu->max_repetitions = ss.host->config.has_value()
                                   ? ss.host->config->bulk_repetitions
                                   : ss.config->has_value()
                                     ? (*ss.config)->bulk_repetitions
                                     : DEFAULT_BULK_REPETITIONS;
          break;
        default:
          break;
      };

      // iterate through each of the next_var_binds in the current partition and add to the PDU
      for (auto&& vb: ss.next_var_binds.front())
        // skip empty var_binds, they are complete
        if (!vb.empty()) {
          snmp_add_null_var(
              pdu,
              (const unsigned long *)vb.data(),
              vb.size()
          );
        }

      // set the state to waiting
      ss.async_status = ASYNC_WAITING;

      // dispatch the PDU, free and log on error
      if (!snmp_sess_async_send(ss.netsnmp_session, pdu, cb, &ss)) {
        char *message;
        int sys_errno;
        int snmp_errno;
        snmp_sess_error(ss.netsnmp_session, &sys_errno, &snmp_errno, &message);
        ss.errors->push_back((SnmpError) {
              SEND_ERROR,
              ss.host->snapshot(),
              sys_errno,
              snmp_errno,
              {},
              {},
              {},
              std::string(message)
        });
        snmp_free_pdu(pdu);
        SNMP_FREE(message);
      }

    }
}

void async_sessions_read(
    std::list<AsyncSession>& sessions
) {

    // iterate through each session
    for (auto&& ss: sessions) {
      // Check that the session is not idle.  A status other than ASYNC_IDLE indicates the
      // response PDU has not been recieved.
      if (ss.async_status == ASYNC_IDLE)
        continue;

      /* The remainder of this code is very specifc to how linux reads socket data and is not
       * specific to net-snmp.  See "man select" for additional information.
       */

      // init a socket set to hold the session socket
      fd_set fdset;
      FD_ZERO(&fdset);

      // init the highest numbered socket id + 1 in the set to 0
      int nfds = 0;  

      // init a timeout parameter
      struct timeval timeout;  

      // init socket reads to be blocking
      int block = NETSNMP_SNMPBLOCK;  

      // let net-snmp fill all the parameters above for select
      snmp_sess_select_info(ss.netsnmp_session, &nfds, &fdset, &timeout, &block);

      // make the syscall to select to read the session socket
      int count = select(nfds, &fdset, NULL, NULL, block ? NULL : &timeout);

      // check if the socket is ready to read
      if (count) {
        // read the socket data; this triggers the callback function
        snmp_sess_read(ss.netsnmp_session, &fdset);
      } else {
        // retry or timeout otherwise
        snmp_sess_timeout(ss.netsnmp_session);
      }
    }

}

void
run(
    PduType pdu_type,
    std::list<Host> hosts,
    std::vector<NullVarBind>& null_var_binds,
    std::vector<std::vector<uint8_t>>& results,
    std::vector<SnmpError>& errors,
    std::optional<Config>& config,
    uint64_t max_active_async_sessions
) {
  
  // Define an active sessions list which MUST be a data structure which does not move the
  // memory location of the sessions.  net-snmp will store the location of the session via a
  // pointer once the PDU is sent.  Using a vector could cause the memory to move as sessions
  // are removed.  Sessions will last multiple iterations of the event loop during retries.
  std::list<AsyncSession> active_sessions;

  // run the event loop until no pending hosts or active sessions are left
  while (!(hosts.empty() && active_sessions.empty())) {
    // remove active sessions with no more work
    close_completed_sessions(active_sessions);

    // move pending hosts to active sessions up to config.max_active_sessions
    while (
        active_sessions.size() <= max_active_async_sessions && !hosts.empty()
    ) {
      // create the AsyncSession and append to active sessions
      create_session(
          pdu_type,
          hosts.front(),
          null_var_binds,
          results,
          errors,
          config,
          active_sessions
      );
      // remove the host from pending hosts
      hosts.pop_front();
    }

    // send the async requests
    async_sessions_send(active_sessions, async_cb);
    // receive the async requests which trigger each session's callback
    async_sessions_read(active_sessions);
  }

}

}
