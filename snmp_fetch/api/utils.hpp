/**
 *  utils.hpp - Utility functions.
 *
 *  To avoid circular imports, this file should not depend on any other imports from this project.
 */

#ifndef NETFRAME__API__UTILS_HPP
#define NETFRAME__API__UTILS_HPP

#include <sstream>
#include <vector>

namespace netframe::api {

/**
 *  oid_to_string - Convert an ObjectIdentity (pointer format) to a string.
 *
 *  @param oid  Pointer to a sequence of uint64_t.
 *  @param size Size of the sequence.
 *  @return     String representation of an ObjectIdentity.
 */
std::string
oid_to_string(uint64_t *oid, size_t oid_size);


/**
 *  oid_to_string - Convert an ObjectIdentity (vector format) to a string.
 *
 *  @param oid  Vector sequence of uint64_t.
 *  @return     String representation of an ObjectIdentity.
 */
std::string
oid_to_string(std::vector<uint64_t> &oid);

}

#endif
