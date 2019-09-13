/**
 *  utils.hpp - Utility functions.
 *
 *  To avoid circular imports, this file should not depend on any other imports from this project.
 */

#ifndef SNMP_FETCH__UTILS_HPP
#define SNMP_FETCH__UTILS_HPP

#include <sstream>
#include <vector>

namespace snmp_fetch {

/**
 *  oid_to_string - Convert an oid (pointer format) to a string.
 *
 *  @param oid  Pointer to a sequence of uint64_t.
 *  @param size Size of the sequence.
 *  @return     String representation of an oid.
 */
std::string
oid_to_string(uint64_t *oid, size_t oid_size) {
  std::ostringstream os;
  for (size_t i = 0; i < oid_size; ++i) os << "." << oid[i];
  return os.str();
}


/**
 *  oid_to_string - Convert an oid (vector format) to a string.
 *
 *  @param oid  Vector sequence of uint64_t.
 *  @return     String representation of an oid.
 */
std::string
oid_to_string(std::vector<uint64_t> &oid) {
  std::ostringstream os;
  for (auto x : oid) os << "." << x;
  return os.str();
}

}

#endif
