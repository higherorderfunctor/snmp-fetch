/**
 * Result processing function definitions.
 */

#ifndef NETFRAME__SNMP__API__RESULTS_HPP
#define NETFRAME__SNMP__API__RESULTS_HPP

#include <map>

#include "types.hpp"

// macro to align a number of bytes to 8 bytes
#define UINT64_ALIGN(x) ((x + 7) & ~0x07)

namespace netframe::snmp::api {

/**
 * Append one response variable binding to the results.
 *
 * @param resp_var_bind Reference to a single response variable binding.
 * @param state         Reference to the response's state wrapped net-snmp session.
 */
void append_result(
    variable_list& resp_var_bind,
    AsyncSession& sessions
);


/**
 * Net-snmp callback function to process async results.
 * 
 * @param op    Op code of this response.
 * @param sp    Pointer to this result's net-snmp session.
 * @param reqid SNMP request ID.
 * @param pdu   Pointer to the result PDU.
 * @param magic Pointer to this result's state wrapped net-snmp session.
 *
 * @return      Always returns 1, errors are handled inside this function.
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
