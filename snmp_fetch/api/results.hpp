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

/**
 *  append_result - Append one response variable binding to the results.
 *
 *  @param resp_var_bind Reference to a single response variable binding.
 *  @param state         Reference to the response's state wrapped net-snmp session.
 */
void append_result(
    variable_list &resp_var_bind,
    async_state &state
);


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
);

}

#endif
