/**
 *  debug.cpp
 */

#include "debug.hpp"

namespace snmp_fetch {

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
 *  print_session
 */
void
print_session(async_state &session) {
  std::cout << "----------------------------------------" << std::endl;
  std::cout << "ASYNC_STATUS: " << session.async_status << std::endl;
  std::cout << "HOST: " << std::get<0>(session.host) << std::endl;
  std::cout << "VAR_BINDS: " << session.var_binds->size() << std::endl;
  std::cout << "NEXT_VAR_BINDS: " << session.next_var_binds.size() << std::endl;
  std::cout << "----------------------------------------" << std::endl;
}

}
