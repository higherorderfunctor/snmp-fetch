/**
 *  session.cpp
 */

#include "session.hpp"

namespace netframe::api {

/**
 *  create_netsnmp_session
 */
void *
create_netsnmp_session(
    host_t &host,
    std::vector<SnmpError> &errors,
    SnmpConfig &config
) {

  // init a net-snmp session template
  netsnmp_session session;
  snmp_sess_init(&session);

  // configure the session template
  session.peername = strdup(std::get<1>(host).c_str());
  session.version = SNMP_VERSION_2c;
  session.retries = (config.retries >= 0) ? config.retries : -1;
  session.timeout = (config.timeout >= 0) ? config.timeout * ONE_SEC : -1;
  session.community = (u_char *)std::get<2>(host).c_str();
  session.community_len = strlen((char *)session.community);

  // open the session
  void *sp = snmp_sess_open(&session);

  // log the error upon session creation failure
  if (sp == NULL) {
    char *message;
    int sys_errno;
    int snmp_errno;
    snmp_error(&session, &errno, &snmp_errno, &message);
    errors.push_back(SnmpError(
          SESSION_ERROR,
          host,
          sys_errno,
          snmp_errno,
          {},
          {},
          {},
          std::string(message)
    ));
    SNMP_FREE(message);
  }

  return sp;

}


/**
 *  create_session
 */
void create_session(
    int pdu_type,
    host_t &host,
    std::vector<var_bind_t> &var_binds,
    std::vector<std::vector<uint8_t>> &results,
    std::vector<SnmpError> &errors,
    SnmpConfig &config,
    std::list<async_state> &sessions
) {

    // create the net-snmp session
    void *session = create_netsnmp_session(host, errors, config);

    // If session creation failed, do not add a state wrapped session.  create_session is
    // responsible for populating the errors list.  The caller is responsible for discarding the
    // host.
    if (session == NULL)
      return;

    // Create a vector of vectors of variable bindings to fetch.  These vectors represent the
    // partitioning of variable bindings by config.max_var_binds_per_pdu.  These variable bindings
    // define the work needed on the session and are seeded with the var_binds from the caller.
    std::vector<std::vector<oid_t>> next_var_binds;
    // iterate through the request var_binds and populate each vector
    for(auto &&vb: var_binds) {
      // if the base vector is empty or max_var_binds_per_pdu has been reached in the last vector,
      // add another partition.
      if (
          next_var_binds.empty() ||
          next_var_binds.back().size() == config.max_var_binds_per_pdu
      )
        next_var_binds.push_back(std::vector<oid_t>());
      // add the var_bind to the last partition
      next_var_binds.back().push_back(std::get<0>(vb));
    }

    // create a state wrapped session for net-snmp callbacks
    auto st = async_state {
      ASYNC_IDLE,
      session,
      pdu_type,
      host,
      &var_binds,
      next_var_binds,  // copy on assignment
      &results,
      &errors,
      &config
    };

    // append the state wrapped session to the sessions list
    sessions.push_back(st);

}


/**
 *  close_completed_sessions
 */
void close_completed_sessions(
    std::list<async_state> &sessions
) {

  // Iterate through all the active sessions. Iterator advancement is controlled manually as the
  // list will be modified in-place during iteration.
  for (auto st = sessions.begin(); st != sessions.end();) {
    auto &session = *st; // dereference the iterator

    // do not process non-idle sessions
    if (session.async_status == ASYNC_IDLE) {
      // check if there are any next_var_bind partitions (potentially defined work)
      if (!session.next_var_binds.empty()) {
        // if there is potential work, verify all var_binds are not empty in the current partition
        if (
            std::all_of(
              session.next_var_binds.front().begin(),
              session.next_var_binds.front().end(),
              [](auto &vb) { return vb.empty(); }
            )
        )
          // If all var_binds are empty, the work is complete, so remove the partition.
          session.next_var_binds.erase(session.next_var_binds.begin());
        // otherwise, rotate the partitions to interleave var_binds from other partitions
        else
          std::rotate(
              session.next_var_binds.begin(),
              session.next_var_binds.begin() + 1,
              session.next_var_binds.end()
          );
      }

      // if there are no partitions left, close the session
      if (session.next_var_binds.empty()) {
        // close the net-snmp session
        snmp_sess_close(session.session);
        // remove the state wrapped session from active sessions
        st = sessions.erase(st);
        // next session is now on this iterator after erasing it; do not incrememnt the iterator
        continue;
      }
    }

    // increment the iterator if no session was closed this iteration
    ++st;
  }

}

}
