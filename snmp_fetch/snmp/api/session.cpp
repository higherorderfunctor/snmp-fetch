/**
 * Session management implementation.
 */

#include "session.hpp"

// TODO might be needed #include <list>
//

extern "C" {
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
}

namespace netframe::snmp::api {

void *
create_netsnmp_session(
    Host& host,
    std::vector<SnmpError>& errors,
    std::optional<Config>& config
) {

  // init a net-snmp session template
  netsnmp_session session;
  snmp_sess_init(&session);

  // configure the session template
  session.peername = strdup(host.hostname.c_str());
  session.retries = host.config.has_value()
                      ? (host.config->retries > 1 ? host.config->retries : 1)
                      : config.has_value()
                        ? (config->retries >= 0 ? config->retries : -1)
                        : DEFAULT_RETRIES;
  session.timeout = host.config.has_value()
                      ? (host.config->timeout > 1 ? host.config->timeout : 1)
                      : config.has_value()
                        ? (config->timeout >= 0 ? config->timeout : -1)
                        : DEFAULT_TIMEOUT;
  session.community = (u_char *)strdup(host.communities.front().string.c_str());
  session.community_len = strlen((char *)session.community);
  session.version = host.communities.front().version;

  // open the session
  void *sp = snmp_sess_open(&session);

  // log the error upon session creation failure
  if (sp == NULL) {
    char *message;
    int sys_errno;
    int snmp_errno;
    snmp_error(&session, &errno, &snmp_errno, &message);
    errors.push_back((SnmpError) {
        SESSION_ERROR,
        host,
        sys_errno,
        snmp_errno,
        {},
        {},
        {},
        std::string(message)
    });
    SNMP_FREE(session.peername);
    SNMP_FREE(session.community);
    SNMP_FREE(message);
  }

  return sp;

}

void create_session(
    PduType pdu_type,
    Host& host,
    std::vector<NullVarBind>& null_var_binds,
    std::vector<std::vector<uint8_t>>& results,
    std::vector<SnmpError>& errors,
    std::optional<Config>& config,
    std::list<AsyncSession>& sessions
) {

    // create the net-snmp session
    void *session = create_netsnmp_session(host, errors, config);

    // If session creation failed, do not add a session.  create_session is responsible for
    // populating the errors list.  The caller is responsible for discarding the host.
    if (session == NULL)
      return;

    // Create a vector of vectors of NullVarBinds to collect.  These vectors represent the
    // partitioning of variable bindings by config.max_var_binds_per_pdu.  These variable bindings
    // define the work needed on the session and are seeded with the var_binds from the caller.
    std::vector<std::vector<ObjectIdentity>> next_var_binds;
    // iterate through the request var_binds and populate each vector
    for(auto&& vb: null_var_binds) {
      // if the base vector is empty or max_var_binds_per_pdu has been reached in the last vector,
      // add another partition.
      if (
          next_var_binds.empty() ||
          next_var_binds.back().size() == (
            config.has_value()
              ? config->var_binds_per_pdu
              : DEFAULT_VAR_BINDS_PER_PDU
          )
      )
        next_var_binds.push_back(std::vector<ObjectIdentity>());
      // add the var_bind to the last partition
      next_var_binds.back().push_back(vb.oid);
    }

    // create a state wrapped session for net-snmp callbacks
    auto st = (AsyncSession) {
      ASYNC_IDLE,
      session,
      pdu_type,
      &host,
      0,
      &null_var_binds,
      next_var_binds,  // copy on assignment
      &results,
      &errors,
      &config
    };

    // append the state wrapped session to the sessions list
    sessions.push_back(st);

}

void close_completed_sessions(
    std::list<AsyncSession>& sessions
) {

  // Iterate through all the sessions. Iterator advancement is controlled manually as the list will
  // be modified in-place during iteration.
  for (auto st = sessions.begin(); st != sessions.end();) {
    // skip non-idle sessions
    if (st->async_status == ASYNC_IDLE) {
      // check if there are any next_var_bind partitions (potentially defined work)
      if (!st->next_var_binds.empty()) {
        // if there is potential work, verify all next_var_binds are non-empty in the current partition
        if (
            std::all_of(
              st->next_var_binds.front().begin(),
              st->next_var_binds.front().end(),
              [](auto& vb) { return vb.empty(); }
            )
        )
          // if all var_binds are empty, the work is complete, so remove the partition
          st->next_var_binds.erase(st->next_var_binds.begin());
        // otherwise, rotate the partitions to interleave var_binds from other partitions
        else
          std::rotate(
              st->next_var_binds.begin(),
              st->next_var_binds.begin() + 1,
              st->next_var_binds.end()
          );
      }

      // if there are no partitions left, close the session
      if (st->next_var_binds.empty()) {
        // close the net-snmp session
        snmp_sess_close(st->netsnmp_session);
        // remove the session
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
