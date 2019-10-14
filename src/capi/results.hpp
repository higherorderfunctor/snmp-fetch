/**
 *  results.hpp - Process async IO results.
 */

#ifndef SNMP_FETCH__RESULTS_HPP
#define SNMP_FETCH__RESULTS_HPP

#include <map>
#include <time.h>
#include <boost/range/combine.hpp>

#include "types.hpp"

extern "C" {
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
}

// macro to align a number of bytes to 8 bytes
#define UINT64_ALIGN(x) ((x + 7) & ~0x07)

namespace snmp_fetch {

std::map<uint8_t, std::string> warning_value_types = {
  {128, "NO_SUCH_OBJECT"},
  {129, "NO_SUCH_INSTANCE"},
  {130, "END_OF_MIB_VIEW"}
};

/**
 *  append_result - Append one response variable binding to the results.
 *
 *  @param resp_var_bind Reference to a single response variable binding.
 *  @param state         Reference to the response's state wrapped net-snmp session.
 */
void append_result(
    variable_list &resp_var_bind,
    async_state &state
) {
  // test for non-value types and generate an error if matched
  /*
  if (warning_value_types.find(resp_var_bind.type) != warning_value_types.end()) {
    oid_t err_var_bind;
    err_var_bind.assign(
        resp_var_bind.name, resp_var_bind.name + resp_var_bind.name_length
    );
    state.errors->push_back(SnmpError(
          VALUE_WARNING,
          state.host,
          {},
          {},
          {},
          {},
          err_var_bind,
          warning_value_types[resp_var_bind.type]
    ));
    return;
  }*/

  // get a timestamp for the result
  time_t timestamp;
  time(&timestamp);

  // find the root variable binding supplied in the initial fetch request for this response
  // variable binding
  auto it = std::find_if(
      state.var_binds->begin(),
      state.var_binds->end(),
      [&resp_var_bind](var_bind_t const &var_bind) {
        // 0 = true; 1 = false
        return !netsnmp_oid_is_subtree(
            std::get<0>(var_bind).data(),
            std::get<0>(var_bind).size(),
            resp_var_bind.name,
            resp_var_bind.name_length
        );
      }
  );

  // if no root variable binding is found, discard the PDU; likely cause for collecting this
  // response is an overrun on a walk
  if (it == state.var_binds->end())
    return;

  // get the index position of the root variable binding from the initial fetch request for this
  // response variable binding
  size_t idx = it - state.var_binds->begin();

  // Get the last recorded response variable binding for the found root variable binding by looking
  // at the associated next_var_binds slot.  Modulus is used due to partitioning with
  // config.max_var_binds_per_pdu.  WARNING: if ambiguous oids are allowed and they cross partitions,
  // this will likely pick the wrong index in the partition and, at worst, segfault
  oid_t &last_var_bind = state.next_var_binds.front()[
    idx % state.config->max_var_binds_per_pdu
  ];

  // discard the response variable binding if the last recorded response variable binding was marked
  // as complete (empty); likely cause for collecting this response is an overrun on a walk
  if (last_var_bind.empty())
    return;

  // Verify the last recorded variable binding has the same root as the response variable binding.
  // If it doesn't, discard the response; a walk likely overran into a slot that exists in another
  // partition.  0 == True, 1 == False
  if (netsnmp_oid_is_subtree(
        std::get<0>(*it).data(),
        std::get<0>(*it).size(),
        last_var_bind.data(),
        last_var_bind.size()
  ))
    return;

  // perform an oid comparison between the response variable binding and the last recorded
  // variable binding
  int oid_test = snmp_oid_compare(
      resp_var_bind.name,
      resp_var_bind.name_length,
      last_var_bind.data(),
      last_var_bind.size()
  );

  // if the oid is lexicographically less than the last recorded variable binding, discard the
  // response; likely cause for collecting this response is an overrun on a walk
  if (oid_test == -1)
    return;

  // if performing a walk, verify the OID is increasing; else discard the response
  if (state.pdu_type != SNMP_MSG_GET && oid_test == 0)
    return;

  // all checks have passed, update the next variable binding for this slot using the response
  // variable binding
  last_var_bind.clear();
  last_var_bind.assign(resp_var_bind.name, resp_var_bind.name + resp_var_bind.name_length);

  // get the oid and result buffer sizes uint64_t aligned
  size_t oid_buffer_size = UINT64_ALIGN(std::get<0>(std::get<1>((*state.var_binds)[idx])));
  size_t result_buffer_size = UINT64_ALIGN(std::get<1>(std::get<1>((*state.var_binds)[idx])));

  // get the struct size of elements in the result slot
  size_t dtype_size = (
      // host index
      sizeof(uint64_t) +
      // oid buffer size (in suboids, not bytes)
      sizeof(uint64_t) +
      // result buffer size (bytes)
      sizeof(uint64_t) +
      // result type code
      sizeof(uint64_t) +
      // timestamp
      sizeof(time_t) +
      // oid buffer
      oid_buffer_size +
      // result buffer
      result_buffer_size
  );

  // increase the result column to copy in the response variable binding
  auto &result = (*state.results)[idx];
  size_t pos = result.size();
  result.resize(pos + dtype_size);

  // copy the host index
  memcpy(
      &result[pos],
      &std::get<0>(state.host),
      sizeof(uint64_t)
  );
  // copy the oid buffer size (in suboids, not bytes)
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
  // copy the oid
  memcpy(
      &result[pos += sizeof(time_t)],
      resp_var_bind.name,
      std::min(oid_buffer_size, resp_var_bind.name_length << 3)
  );
  // copy the result
  memcpy(
      &result[pos += oid_buffer_size],
      resp_var_bind.val.bitstring,
      // Use the caller's buffer size for the result instead of the uint64_t aligned
      // result_buffer_size.  This allows the caller to add up to 7 bytes of padding and is
      // useful for cstrings that expect to be null terminated.  Example: A 255 byte buffer will
      // be copied into a 256 byte uint64_t aligned buffer with the last byte padded to 0.
      std::min(result_buffer_size, resp_var_bind.val_len)
  );
}


/**
 *  async_cb - Callback function to process async results.
 *  
 *  @param op    Op code of this response.
 *  @param sp    Pointer to this result's net-snmp session.
 *  @param reqid SNMP request ID.
 *  @param pdu   Pointer to the result PDU.
 *  @param magic Pointer to this result's state wrapped net-snmp session.
 *
 *  @return      Always returns 1, errors are handled inside this function.
 */
int async_cb(
    int op,
    snmp_session *sp,
    int reqid,
    snmp_pdu *pdu,
    void *magic
) {

  // deconstruct the state
  auto &state = *(async_state *)magic;

  // set the status to idle since response PDU has been collected
  state.async_status = ASYNC_IDLE;

  // create a reference to the last collected variable bindings in the current
  // parition (copy on assignment)
  std::vector<oid_t> last_var_binds = state.next_var_binds.front();

  // handle each op code
  switch (op) {
    case NETSNMP_CALLBACK_OP_RECEIVED_MESSAGE:
      // check that the PDU was allocated
      if (pdu) {
        // check the correct type of PDU was returned in the response
        if (pdu->command == SNMP_MSG_RESPONSE) {
          // check the PDU doesn't have an error status
          if (pdu->errstat == SNMP_ERR_NOERROR) {
            // append each response variable binding to the results
            for(variable_list *var = pdu->variables; var; var = var->next_variable) {
              append_result(*var, state);
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
            oid_t err_var_bind;
            err_var_bind.assign(vp->name, vp->name + vp->name_length);
            state.errors->push_back(SnmpError(
                  BAD_RESPONSE_PDU_ERROR,
                  state.host,
                  {},
                  {},
                  pdu->errstat,
                  pdu->errindex,
                  err_var_bind,
                  std::string(snmp_errstring(pdu->errstat))
            ));
            // clear all work for this session
            state.next_var_binds.clear();
          }
        } else {
          state.errors->push_back(SnmpError(
                BAD_RESPONSE_PDU_ERROR,
                state.host,
                {},
                SNMPERR_PROTOCOL,
                {},
                {},
                {},
                "Expected RESPONSE-PDU but got " +
                std::string(snmp_pdu_type(pdu->command)) +
                "-PDU"
          ));
          // clear all work for this session
          state.next_var_binds.clear();
        }
      } else {
        state.errors->push_back(SnmpError(
              CREATE_RESPONSE_PDU_ERROR,
              state.host,
              {},
              {},
              {},
              {},
              {},
              "Failed to allocate memory for the response PDU"
        ));
        // clear all work for this session
        state.next_var_binds.clear();
      }
      break;
    case NETSNMP_CALLBACK_OP_TIMED_OUT:
      state.errors->push_back(SnmpError(
            TIMEOUT_ERROR,
            state.host,
            {},
            SNMPERR_TIMEOUT,
            {},
            {},
            {},
            "Timeout error"
      ));
      // clear all work for this session
      state.next_var_binds.clear();
      break;
    case NETSNMP_CALLBACK_OP_SEND_FAILED:
      state.errors->push_back(SnmpError(
            ASYNC_PROBE_ERROR,
            state.host,
            {},
            {},
            {},
            {},
            {},
            "Async probe error"
      ));
      // clear all work for this session
      state.next_var_binds.clear();
      break;
    case NETSNMP_CALLBACK_OP_DISCONNECT:
      state.errors->push_back(SnmpError(
            TRANSPORT_DISCONNECT_ERROR,
            state.host,
            std::nullopt,
            SNMPERR_ABORT,
            {},
            {},
            {},
            "Transport disconnect error"
      ));
      // clear all work for this session
      state.next_var_binds.clear();
      break;
    case NETSNMP_CALLBACK_OP_RESEND:
      // set the status to retry
      state.async_status = ASYNC_RETRY;
      break;
  }

  // validate work for the next pdu if the session is idle and the work isn't already completed
  if (state.async_status == ASYNC_IDLE && !state.next_var_binds.empty())
    // zip the work that generated this request with the proposed work found when appending the
    // results
    for (
        auto const &&[last_oid, tail]:
        boost::combine(last_var_binds, state.next_var_binds.front())
    ) {
      auto &next_oid = boost::get<0>(tail);  // deconstruct the (next_oid, nil) tuple
      // if result oid did not increase from the request oid, mark the slot to no longer
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

#endif
