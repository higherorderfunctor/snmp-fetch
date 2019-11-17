/**
 *  utils.cpp
 */

#include "utils.hpp"

namespace snmp_fetch {

/**
 *  oid_to_string
 */
std::string
oid_to_string(uint64_t *oid, size_t oid_size) {
  std::ostringstream os;
  for (size_t i = 0; i < oid_size; ++i) os << "." << oid[i];
  return os.str();
}


/**
 *  oid_to_string
 */
std::string
oid_to_string(std::vector<uint64_t> &oid) {
  std::ostringstream os;
  for (auto x : oid) os << "." << x;
  return os.str();
}

}
