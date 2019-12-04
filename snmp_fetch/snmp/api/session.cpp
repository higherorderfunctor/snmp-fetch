/**
 * Session management implementation.
 */

#include "session.hpp"

#include <algorithm>

extern "C" {
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <debug.h>
}

namespace netframe::snmp::api {

void*
create_netsnmp_session(
    const Host& host,
    std::vector<SnmpError>& errors,
    const std::optional<Config>& config
) {

  // init a net-snmp session template
  netsnmp_session session;
  snmp_sess_init(&session);

  // configure the session template
  session.peername = strdup(host.hostname.c_str());
  session.retries = host.config.has_value()
                      ? ( host.config->retries >= 0 ? host.config->retries : -1 )
                      : config.has_value()
                        ? ( config->retries >= 0 ? config->retries : -1 )
                        : DEFAULT_RETRIES;
  session.timeout = host.config.has_value()
                      ? (host.config->timeout >= 0 ? host.config->timeout * ONE_SEC : -1 )
                      : config.has_value()
                        ? ( config->timeout >= 0 ? config->timeout * ONE_SEC : -1 )
                        : DEFAULT_TIMEOUT;
  session.community = (u_char *)strdup(host.communities.front().string.c_str());
  session.community_len = strlen((char *)session.community);
  session.version = host.communities.front().version;

  // open the session
  void* sptr = snmp_sess_open(&session);

  DB_TRACELOC(0, "SESSION_ADDRESS: %u\n", sptr);

  // log the error upon session creation failure
  if (sptr == NULL) {
    char *message;
    int sys_errno;
    int snmp_errno;
    snmp_error(&session, &errno, &snmp_errno, &message);
    errors.push_back((SnmpError) {
        SESSION_ERROR,
        host.snapshot(),
        sys_errno,
        snmp_errno,
        {},
        {},
        {},
        std::string(message)
    });
    DB_TRACELOC(0, "%s\n", errors.back().to_string().c_str());
    SNMP_FREE(session.peername);
    SNMP_FREE(session.community);
    SNMP_FREE(message);
  } else {
    DB_TRACELOC(0, "SESSION_HOSTNAME: %s\n", session.peername);
    DB_TRACELOC(0, "SESSION_VERSION: %u\n", session.version);
    DB_TRACELOC(0, "SESSION_COMMUNITY: %s\n", session.community);
    DB_TRACELOC(0, "SESSION_COMMUNITY_LENGTH: %u\n", session.community_len);
    DB_TRACELOC(0, "SESSION_RETRIES: %d\n", session.retries);
    DB_TRACELOC(0, "SESSION_TIMEOUT: %d\n", session.timeout);
  }

  return sptr;

}

void create_session(
    const PduType pdu_type,
    const Host& host,
    const std::vector<NullVarBind>& null_var_binds,
    std::vector<std::vector<uint8_t>>& results,
    std::vector<SnmpError>& errors,
    const std::optional<Config>& config,
    std::list<AsyncSession>& active_sessions
) {

    void* sptr = create_netsnmp_session(host, errors, config);

    // If session creation failed, do not add a session.  create_session is responsible for
    // populating the errors list; the caller is responsible for discarding the host.
    if (sptr == NULL)
      return;

    // Create a vector of vectors of ObjectIdentities to collect.  These vectors represent the
    // partitioning of OIDs by that define the work needed on the session and are seeded with
    // the null_var_binds from the caller.
    std::vector<std::vector<ObjectIdentity>> next_object_identities;
    // iterate through the request null_var_binds and populate each vector
    for(auto&& vt: null_var_binds) {
      // if the base vector is empty or var_binds_per_pdu has been reached in the last vector,
      // add another partition.
      if (
          next_object_identities.empty() ||
          next_object_identities.back().size() == (
            host.config.has_value()
              ? host.config->var_binds_per_pdu
              : config.has_value()
                ? config->var_binds_per_pdu
                : DEFAULT_VAR_BINDS_PER_PDU
          )
      )
        next_object_identities.push_back(std::vector<ObjectIdentity>());
      // add the var_bind to the last partition
      next_object_identities.back().push_back(vt.oid);
    }

    // append the session to the active sessions list
    active_sessions.push_back((AsyncSession) {
      ASYNC_IDLE,
      sptr,
      pdu_type,
      host,
      0,
      &null_var_binds,
      next_object_identities,
      &results,
      &errors,
      &config
    });

}

void close_completed_sessions(
    std::list<AsyncSession>& sessions
) {

  // Iterate through all the sessions. Iterator advancement is controlled manually as the list will
  // be modified in-place during iteration.
  for (auto st = sessions.begin(); st != sessions.end();) {
    // skip non-idle sessions
    if (st->async_status == ASYNC_IDLE) {
      // check if there are any partitions (potentially defined work)
      if (!st->next_object_identities.empty()) {
        // if there is potential work, verify all OIDs are non-empty in the current partition
        if (
            std::all_of(
              st->next_object_identities.front().begin(),
              st->next_object_identities.front().end(),
              [](auto& oid) { return oid.empty(); }
            )
        )
          // if all var_binds are empty, the work is complete, so remove the partition
          st->next_object_identities.erase(st->next_object_identities.begin());
        // otherwise, rotate the partitions to interleave var_binds from other partitions
        else
          std::rotate(
              st->next_object_identities.begin(),
              st->next_object_identities.begin() + 1,
              st->next_object_identities.end()
          );
      }

      // if there are no partitions left, close the session
      if (st->next_object_identities.empty()) {
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
