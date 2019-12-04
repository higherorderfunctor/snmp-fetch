/**
 *  Async function implementations.
 */

#include "asyncio.hpp"

#include "session.hpp"

extern "C" {
#include <debug.h>
}

namespace netframe::snmp::api {

void async_sessions_send(
    std::list<AsyncSession>& sessions,
    const netsnmp_callback cb
) {

    // iterate through each session
    for (auto&& st: sessions) {
      // skip sessions that are not idle
      if (st.async_status != ASYNC_IDLE)
        continue;

      // create the request PDU
      netsnmp_pdu *pdu = snmp_pdu_create(st.pdu_type);

      // log PDU creation failures
      if (!pdu) {
        st.errors->push_back((SnmpError) {
              CREATE_REQUEST_PDU_ERROR,
              st.host.snapshot(),
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
      switch (st.pdu_type) {
        case BULKGET:
          pdu->non_repeaters = 0;
          pdu->max_repetitions = st.host.config.has_value()
                                   ? st.host.config->bulk_repetitions
                                   : st.config->has_value()
                                     ? (*st.config)->bulk_repetitions
                                     : DEFAULT_BULK_REPETITIONS;
          break;
        default:
          break;
      };

      // iterate through each of the next_var_binds in the current partition and add to the PDU
      for (auto&& ot: st.next_object_identities.front())
        // skip empty var_binds, they are complete
        if (!ot.empty()) {
          snmp_add_null_var(
              pdu,
              ot.data(),
              ot.size()
          );
        }

      // set the state to waiting
      st.async_status = ASYNC_WAITING;

      // dispatch the PDU, free and log on error
      if (!snmp_sess_async_send(st.netsnmp_session, pdu, cb, &st)) {
        char *message;
        int sys_errno;
        int snmp_errno;
        snmp_sess_error(st.netsnmp_session, &sys_errno, &snmp_errno, &message);
        st.errors->push_back((SnmpError) {
              SEND_ERROR,
              st.host.snapshot(),
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
    const std::list<AsyncSession>& sessions
) {

    // iterate through each session
    for (auto&& st: sessions) {
      // Check that the session is not idle.  A status other than ASYNC_IDLE indicates the
      // response PDU has not been recieved.
      if (st.async_status == ASYNC_IDLE)
        continue;

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
      snmp_sess_select_info(st.netsnmp_session, &nfds, &fdset, &timeout, &block);
      DB_TRACELOC(0, "SELECTED_TIMEOUT: %d.%d\n", timeout.tv_sec, timeout.tv_usec);

      // make the syscall to select to read the session socket
      int count = select(nfds, &fdset, NULL, NULL, block ? NULL : &timeout);

      // check if the socket is ready to read
      if (count) {
        // read the socket data; this triggers the callback function
        DB_TRACELOC(0, "READ_SOCKET: %s\n", st.host.snapshot().to_string().c_str());
        snmp_sess_read(st.netsnmp_session, &fdset);
      } else {
        // retry or timeout otherwise
        DB_TRACELOC(0, "TIMEOUT_OR_RETRY_SOCKET: %s\n", st.host.snapshot().to_string().c_str());
        snmp_sess_timeout(st.netsnmp_session);
      }
    }

}

void
run(
    const PduType pdu_type,
    const std::vector<Host>& hosts,
    const std::vector<NullVarBind>& null_var_binds,
    std::vector<std::vector<uint8_t>>& results,
    std::vector<SnmpError>& errors,
    const std::optional<Config>& config,
    const uint64_t max_active_async_sessions
) {
  
  // Define an active sessions list which MUST be a data structure which does not move the
  // memory location of the sessions.  net-snmp will store the location of the session via a
  // pointer once the PDU is sent.  Using a vector could cause the memory to move as sessions
  // are removed.  Sessions will last multiple iterations of the event loop during retries.
  std::list<AsyncSession> active_sessions;

  auto ht = hosts.begin();

  // run the event loop until no pending hosts or active sessions are left
  while (ht != hosts.end() || !active_sessions.empty()) {
    // remove active sessions with no more work
    close_completed_sessions(active_sessions);

    // move pending hosts to active sessions up to config.max_active_sessions
    while (
        active_sessions.size() <= max_active_async_sessions && ht != hosts.end()
    ) {
      // create the AsyncSession and append to active sessions
      create_session(
          pdu_type,
          *ht,
          null_var_binds,
          results,
          errors,
          config,
          active_sessions
      );
      // remove the host from pending hosts
      ht = std::next(ht);
    }

    // send the async requests
    async_sessions_send(active_sessions, async_cb);
    // receive the async requests which trigger each session's callback
    async_sessions_read(active_sessions);
  }

}

}
