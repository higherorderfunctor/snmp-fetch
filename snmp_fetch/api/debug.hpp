/**
 *  debug.hpp - Debug functions.
 */

#ifndef NETFRAME__API__DEBUG_HPP
#define NETFRAME__API__DEBUG_HPP

#include <iostream>

#include "types.hpp"
#include "utils.hpp"

namespace netframe::api {

/**
 *  print_oid - Debug print an OID.
 *
 *  @param oid  Pointer to a sequence of uint64_t.
 *  @param size Size of the sequence.
 */
void
print_oid(uint64_t *oid, size_t oid_size);


/**
 *  print_async_state - Debug print an AsyncState.
 *
 *  @param session Reference to an AsyncState.
 */
void
print_async_state(AsyncState &state);

}

#endif
