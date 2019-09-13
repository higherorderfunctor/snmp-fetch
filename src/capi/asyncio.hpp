/**
 *  asyncio.hpp - Async IO handlers.
 */

#ifndef SNMP_FETCH__ASYNCIO_HPP
#define SNMP_FETCH__ASYNCIO_HPP

#include "results.hpp"
#include "session.hpp"

namespace snmp_fetch {

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
) {

    // iterate through each session
    for (auto &&st: sessions) {
      // skip session that are not idle
      if (st.async_status != ASYNC_IDLE)
        continue;

      // create the request PDU
      netsnmp_pdu *pdu = snmp_pdu_create(st.pdu_type);

      // log PDU creation failures
      if (!pdu) {
        st.errors->push_back(SnmpError(
              CREATE_REQUEST_PDU_ERROR,
              st.host,
              {},
              {},
              {},
              {},
              {},
              "Failed to allocate memory for the request PDU"
        ));
        return;
      }

      // set PDU options based on PDU type
      switch (st.pdu_type) {
        case SNMP_MSG_GETBULK:
          pdu->non_repeaters = 0;
          pdu->max_repetitions = st.config->max_bulk_repetitions;
          break;
      };

      // iterate through each of the next_var_binds in the current partition and add to the PDU
      for (auto &&vb: st.next_var_binds.front())
        // skip empty var_binds, they are complete
        if (!vb.empty()) {
          snmp_add_null_var(
              pdu,
              (const unsigned long *)vb.data(),
              vb.size()
          );
        }

      // set the state to waiting
      st.async_status = ASYNC_WAITING;

      // dispatch the PDU, free and log on error
      if (!snmp_sess_async_send(st.session, pdu, cb, &st)) {
        char *message;
        int sys_errno;
        int snmp_errno;
        snmp_sess_error(&st.session, &sys_errno, &snmp_errno, &message);
        st.errors->push_back(SnmpError(
              SEND_ERROR,
              st.host,
              sys_errno,
              snmp_errno,
              {},
              {},
              {},
              std::string(message)
        ));
        snmp_free_pdu(pdu);
        SNMP_FREE(message);
      }

    }
}


/**
 *  async_sessions_read - Read all sockets for response PDUs.
 *
 *  @param sessions Reference to a list of state wrapped net-snmp sessions.  This function checks
 *  each for response PDUs which triggers the callback function on the session.
 */
void async_sessions_read(
    std::list<async_state> &sessions
) {

    // iterate through each session
    for (auto &&st: sessions) {
      // Check that the session is not idle.  This function triggers the callback which is
      // responsible for setting the status.  A state other than ASYNC_IDLE indicates the
      // response PDU has not been read and processed.
      if (st.async_status == ASYNC_IDLE)
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
      snmp_sess_select_info(st.session, &nfds, &fdset, &timeout, &block);

      // make the syscall to select to read the session socket
      int count = select(nfds, &fdset, NULL, NULL, block ? NULL : &timeout);

      // check if the socket is ready to read
      if (count) {
        // read the socket data; this triggers the callback function
        snmp_sess_read(st.session, &fdset);
      } else {
        // retry or timeout otherwise, this also triggers the callback function for both
        // cases with the appropriate op code in the callback
        snmp_sess_timeout(st.session);
      }
    }

}


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
    Config &config
) {
  
  // do NOT init net-snmp to disable config loading and mib processing
  //init_snmp("snmp_fetch");

  // init a list of pending hosts in reverse to work back to front to reduce copies as hosts are
  // removed
  std::vector<host_t> pending_hosts(hosts.size());
  std::reverse_copy(hosts.begin(), hosts.end(), pending_hosts.begin());

  // Define an active sessions list which MUST be a data structure which does not move the
  // memory location of the sessions.  net-snmp will store the location of the session via a
  // pointer once the PDU is sent.  Using a vector could cause the memory to move as sessions
  // are removed.  Sessions will last multiple iterations of the event loop during retries.
  std::list<async_state> active_sessions;

  // run the event loop until no pending hosts/active sessions are left
  while (!(pending_hosts.empty() && active_sessions.empty())) {
    // remove active sessions with no more work
    close_completed_sessions(active_sessions);

    // Move pending hosts to active sessions up to config.max_active_sessions.  Pending hosts
    // should be consumed from the back else the entire pending hosts vector will need to be moved
    // in memory.
    while (
        active_sessions.size() <= config.max_active_sessions
        && !pending_hosts.empty()
    ) {
      // Create the state wrapped net-snmp session and append to active sessions.  If this fails
      // the append will not occur and the host will be discarded.  create_session is responsible
      // for logging the error.
      create_session(
          pdu_type,
          pending_hosts.back(),
          var_binds,
          results,
          errors,
          config,
          active_sessions
      );
      // remove the host from pending hosts
      pending_hosts.erase(pending_hosts.end() - 1);
    }

    // send the async requests
    async_sessions_send(active_sessions, async_cb);
    // receive the async requests which triggers the session's callback
    async_sessions_read(active_sessions);
  }

}

}

#endif
