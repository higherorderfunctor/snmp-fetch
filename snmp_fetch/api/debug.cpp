/**
 *  debug.cpp
 */

#include "debug.hpp"

namespace netframe::api {

/**
 *  print_oid
 */
void
print_oid(uint64_t *oid, size_t oid_size) {
  std::cerr << "DEBUG_OID: "
    << oid_size
    << ": "
    << oid_to_string(oid, oid_size)
    << std::endl;
}


/**
 *  print_async_state
 */
void
print_async_state(AsyncState &state) {
  std::cout << "----------------------------------------" << std::endl;
  std::cout << "ASYNC_STATUS: " << state.async_status << std::endl;
  std::cout << "HOST: " << state.host.to_string() << std::endl;
  std::cout << "VAR_BINDS: " << state.var_binds->size() << std::endl;
  std::cout << "NEXT_VAR_BINDS: " << state.next_var_binds.size() << std::endl;
  std::cout << "----------------------------------------" << std::endl;
}

}
