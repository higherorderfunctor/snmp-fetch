/**
 * Utility function implementations.
 */

#include "utils.hpp"

namespace netframe::snmp::api {

std::string
oid_to_string(const uint64_t* oid, const size_t oid_size) {
  std::ostringstream os;
  for (size_t i = 0; i < oid_size; ++i) os << "." << oid[i];
  return os.str();
}

std::string
oid_to_string(const std::vector<uint64_t>& oid) {
  return oid_to_string(oid.data(), oid.size());
}

}
