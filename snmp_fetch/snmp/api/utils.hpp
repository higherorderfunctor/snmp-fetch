/**
 * Utility function definitions.
 */

#ifndef NETFRAME__SNMP__API__UTILS_HPP
#define NETFRAME__SNMP__API__UTILS_HPP

#include <sstream>
#include <vector>

namespace netframe::snmp::api {

/**
 * Convert an ObjectIdentity (pointer format) to a string.
 *
 * @param oid  Pointer to a sequence of uint64_t.
 * @param size Size of the sequence.
 * @return     String representation of an ObjectIdentity.
 */
std::string
oid_to_string(const uint64_t* oid, const size_t oid_size);


/**
 * Convert an ObjectIdentity (vector format) to a string.
 *
 * @param oid  Vector sequence of uint64_t.
 * @return     String representation of an ObjectIdentity.
 */
std::string
oid_to_string(const std::vector<uint64_t>& oid);

}

#endif
