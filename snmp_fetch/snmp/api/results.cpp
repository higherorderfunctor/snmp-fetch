/**
 * Result processing implementations.
 */

#include "results.hpp"

#include <map>
#include <time.h>
#include <boost/range/combine.hpp>
#include <iostream>  // TODO remove

extern "C" {
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <debug.h>
}

namespace netframe::snmp::api {

std::map<uint8_t, std::string> WARNING_VALUE_TYPES = {
  {128, "NO_SUCH_OBJECT"},
  {129, "NO_SUCH_INSTANCE"},
  {130, "END_OF_MIB_VIEW"}
};

void append_result(
    variable_list& resp_var_bind,
    AsyncSession& session
) {
  // test for non-value types and generate an error if matched
  if (WARNING_VALUE_TYPES.find(resp_var_bind.type) != WARNING_VALUE_TYPES.end()) {
    ObjectIdentity err_var_bind;
    err_var_bind.assign(
        resp_var_bind.name, resp_var_bind.name + resp_var_bind.name_length
    );
    session.errors->push_back((SnmpError) {
          VALUE_WARNING,
          session.host.snapshot(),
          {},
          {},
          {},
          {},
          err_var_bind,
          WARNING_VALUE_TYPES[resp_var_bind.type]
    });
    return;
  }

  // get a timestamp for the response
  time_t timestamp;
  time(&timestamp);

  // find the null variable binding supplied in the initial request for this response variable
  // binding
  auto it = std::find_if(
      session.null_var_binds->begin(),
      session.null_var_binds->end(),
      [&resp_var_bind](const NullVarBind& null_var_bind) {
        // 0 = true; 1 = false
        return !netsnmp_oid_is_subtree(
            null_var_bind.oid.data(),
            null_var_bind.oid.size(),
            resp_var_bind.name,
            resp_var_bind.name_length
        );
      }
  );

  // if no root variable binding is found, discard the response; likely cause for collecting this
  // response is an overrun on a walk
  if (it == session.null_var_binds->end())
    return;

  // get the index position of the root variable binding for this response variable binding
  size_t idx = it - session.null_var_binds->begin();

  // Get the last recorded response variable binding for the found root variable binding by looking
  // at the associated next_object_identities slot.  Modulus is used due to partitioning with
  // var_binds_per_pdu.  WARNING: if ambiguous OIDs are allowed and they cross partitions,
  // this will likely pick the wrong index in the partition and, at worst, segfault.
  auto& last_var_bind = session.next_object_identities.front()[
    idx % (session.config->has_value() ? (*session.config)->var_binds_per_pdu : DEFAULT_VAR_BINDS_PER_PDU)
  ];

  // discard the response variable binding if the last recorded response variable binding was marked
  // as complete (empty); likely cause for collecting this response is an overrun on a walk
  if (last_var_bind.empty())
    return;

  // Verify the last recorded variable binding has the same root as the response variable binding.
  // If it doesn't, discard the response; a walk likely overran into a slot that exists in another
  // partition.  0 == True, 1 == False
  if (netsnmp_oid_is_subtree(
        it->oid.data(),
        it->oid.size(),
        last_var_bind.data(),
        last_var_bind.size()
  ))
    return;

  // perform an OID comparison between the response variable binding and the last recorded
  // variable binding
  int oid_test = snmp_oid_compare(
      resp_var_bind.name,
      resp_var_bind.name_length,
      last_var_bind.data(),
      last_var_bind.size()
  );

  // if the OID is lexicographically less than the last recorded variable binding, discard the
  // response; likely cause for collecting this response is an overrun on a walk from another root
  // variable binding
  if (oid_test == -1)
    return;

  // if performing a walk, verify the OID is increasing; else discard the response
  if (session.pdu_type != SNMP_MSG_GET && oid_test == 0)
    return;

  // all checks have passed, update the next variable binding for this slot using the response
  // variable binding
  last_var_bind.clear();
  last_var_bind.assign(resp_var_bind.name, resp_var_bind.name + resp_var_bind.name_length);

  // get the OID and value buffer sizes uint64_t aligned
  size_t oid_buffer_size = UINT64_ALIGN((*session.null_var_binds)[idx].oid_size);
  size_t value_buffer_size = UINT64_ALIGN((*session.null_var_binds)[idx].value_size);

  // get the struct size of elements in the result slot
  size_t dtype_size = (
      // host id
      sizeof(uint64_t) +
      // community index
      sizeof(uint64_t) +
      // oid buffer size (in suboids, not bytes)
      sizeof(uint64_t) +
      // value buffer size (bytes)
      sizeof(uint64_t) +
      // value type code
      sizeof(uint64_t) +
      // timestamp
      sizeof(time_t) +
      // oid buffer
      oid_buffer_size +
      // value buffer
      value_buffer_size
  );

  // increase the response column to copy in the response variable binding
  auto &result = (*session.results)[idx];
  size_t pos = result.size();
  result.resize(pos + dtype_size);

  // copy the host id
  memcpy(
      &result[pos],
      &session.host.id,
      sizeof(uint64_t)
  );
  // copy the community index
  memcpy(
      &result[pos += sizeof(uint64_t)],
      &session.community_index,
      sizeof(uint64_t)
  );
  // copy the OID buffer size (in suboids, not bytes)
  memcpy(
      &result[pos += sizeof(uint64_t)],
      &resp_var_bind.name_length,
      sizeof(uint64_t)
  );
  // copy the result buffer size (bytes)
  memcpy(
      &result[pos += sizeof(uint64_t)],
      &resp_var_bind.val_len,
      sizeof(uint64_t)
  );
  // copy the result type code
  memcpy(
    &result[pos += sizeof(uint64_t)],
    &resp_var_bind.type,
    sizeof(uint64_t)
  );
  // copy the timestamp
  memcpy(
    &result[pos += sizeof(uint64_t)],
    &timestamp,
    sizeof(time_t)
  );
  // copy the OID
  memcpy(
      &result[pos += sizeof(time_t)],
      resp_var_bind.name,
      std::min(oid_buffer_size, resp_var_bind.name_length << 3)
  );
  // copy the value
  memcpy(
      &result[pos += oid_buffer_size],
      resp_var_bind.val.bitstring,
      std::min(value_buffer_size, resp_var_bind.val_len)
  );
}


int async_cb(
    int op,
    snmp_session *sp,
    int reqid,
    snmp_pdu *pdu,
    void *magic
) {

  DB_TRACELOC(0, "PDU_RCV_OP_CODE: %d\n", op);

  // deconstruct the session
  auto& session = *(AsyncSession *)magic;

  // set the status to idle since response PDU has been collected
  session.async_status = ASYNC_IDLE;

  // create a reference to the last collected variable bindings in the current
  // parition (copy on assignment)
  std::vector<ObjectIdentity> last_var_binds = session.next_object_identities.front();

  // handle each op code
  switch (op) {
    case NETSNMP_CALLBACK_OP_RECEIVED_MESSAGE:
      DB_TRACE(0, "CALLBACK_OP_RECEIVED_MESSAGE: %s\n", session.host.snapshot().to_string().c_str());
      // check that the PDU was allocated
      if (pdu) {
        // check the correct type of PDU was returned in the response
        if (pdu->command == SNMP_MSG_RESPONSE) {
          // check the PDU doesn't have an error status
          if (pdu->errstat == SNMP_ERR_NOERROR) {
            // append each response variable binding to the results
            for(variable_list *var = pdu->variables; var; var = var->next_variable) {
              append_result(*var, session);
            }
          } else {
            // find the variable binding with an error
            int ix;
            variable_list *vp;
            for (
                ix = 1, vp = pdu->variables;
                vp && ix != pdu->errindex;
                vp = vp->next_variable, ++ix
            );
            ObjectIdentity err_var_bind;
            err_var_bind.assign(vp->name, vp->name + vp->name_length);
            session.errors->push_back((SnmpError) {
                  BAD_RESPONSE_PDU_ERROR,
                  session.host.snapshot(),
                  {},
                  {},
                  pdu->errstat,
                  pdu->errindex,
                  err_var_bind,
                  std::string(snmp_errstring(pdu->errstat))
            });
            // clear all work for this session
            session.next_object_identities.clear();
          }
        } else {
          session.errors->push_back((SnmpError) {
              BAD_RESPONSE_PDU_ERROR,
              session.host.snapshot(),
              {},
              SNMPERR_PROTOCOL,
              {},
              {},
              {},
              "Expected RESPONSE-PDU but got " +
              std::string(snmp_pdu_type(pdu->command)) +
              "-PDU"
          });
          // clear all work for this session
          session.next_object_identities.clear();
        }
      } else {
      DB_TRACE(0, "CALLBACK_OP_PDU_ERROR: %s\n", session.host.snapshot().to_string().c_str());
        session.errors->push_back((SnmpError) {
            CREATE_RESPONSE_PDU_ERROR,
            session.host.snapshot(),
            {},
            {},
            {},
            {},
            {},
            "Failed to allocate memory for the response PDU"
        });
        // clear all work for this session
        session.next_object_identities.clear();
      }
      break;
    case NETSNMP_CALLBACK_OP_TIMED_OUT:
      DB_TRACE(0, "CALLBACK_OP_TIMED_OUT: %s\n", session.host.snapshot().to_string().c_str());
      session.errors->push_back((SnmpError) {
            TIMEOUT_ERROR,
            session.host.snapshot(),
            {},
            SNMPERR_TIMEOUT,
            {},
            {},
            {},
            "Timeout error"
      });
      // clear all work for this session
      session.next_object_identities.clear();
      break;
    case NETSNMP_CALLBACK_OP_SEND_FAILED:
      DB_TRACE(0, "CALLBACK_OP_SEND_FAILED: %s\n", session.host.snapshot().to_string().c_str());
      session.errors->push_back((SnmpError) {
            ASYNC_PROBE_ERROR,
            session.host.snapshot(),
            {},
            {},
            {},
            {},
            {},
            "Async probe error"
      });
      // clear all work for this session
      session.next_object_identities.clear();
      break;
    case NETSNMP_CALLBACK_OP_DISCONNECT:
      DB_TRACE(0, "CALLBACK_OP_DISCONNECT: %s\n", session.host.snapshot().to_string().c_str());
      session.errors->push_back((SnmpError) {
            TRANSPORT_DISCONNECT_ERROR,
            session.host.snapshot(),
            std::nullopt,
            SNMPERR_ABORT,
            {},
            {},
            {},
            "Transport disconnect error"
      });
      // clear all work for this session
      session.next_object_identities.clear();
      break;
    case NETSNMP_CALLBACK_OP_RESEND:
      // set the status to retry
			std::cout <<  session.host.to_string() << std::endl;
      DB_TRACE(0, "CALLBACK_OP_RESEND: %s\n", session.host.snapshot().to_string().c_str());
      session.async_status = ASYNC_RETRY;
      break;
  }

  // validate work for the next PDU if the session is idle and the work isn't already completed
  if (session.async_status == ASYNC_IDLE && !session.next_object_identities.empty())
    // zip the work that generated this request with the proposed work found when appending the
    // results
    for (
        const auto &&[last_oid, tail]:
        boost::combine(last_var_binds, session.next_object_identities.front())
    ) {
      auto& next_oid = boost::get<0>(tail);  // deconstruct the (OID, nil) tuple
      // if result OID did not increase from the request OID, mark the slot to no longer
      // collect; it was either a get request or a walk request that has been exhausted
      if (snmp_oid_compare(
          next_oid.data(),
          next_oid.size(),
          last_oid.data(),
          last_oid.size()
      ) != 1)
        next_oid.clear();
    }

  return 1;

}

}
