/**
 * Main entry point definition for the python C++ extension.
 */

#ifndef NETFRAME__API__CAPIMODULE_HPP
#define NETFRAME__API__CAPIMODULE_HPP

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "types.hpp"

namespace py = pybind11;

namespace netframe::api {

/**
 * Wraps a C++ sequence in a numpy array.  This object will free the underlying data when the
 * numpy array is garbage collected.
 *
 * @param seq Sequence to be wrapped in a numpy array.
 * @return    Numpy array.
 */
template <typename Sequence>
inline py::array_t<typename Sequence::value_type>
as_pyarray(Sequence& seq);


/**
 * Python interface for making an SNMP request.
 *
 * @param pdu_type             GET, GETNEXT, or GETBULK.
 * @param hosts                A list Hosts.
 * @param var_binds            A list of NullVarBinds.
 * @param config               An optional SnmpConfig.
 * @param max_active_sessions  An optional value indicate the maximum number of asynchronous sessions.
 * @return                     A tuple of (results, errors).
 *
 * Results is a vector of structured numpy arrays, one per NullVarBind.
 *     uint64_t host index      - Index of the host
 *     uint64_t community index - Index of the community string used
 *     uint64_t oid size        - Number of uint64_t sub-OIDs
 *     uint64_t value size      - Size of the SNMP object in bytes
 *     uint64_t value type      - SNMP object type code
 *     [uint64_t] oid           - Object identity
 *     [uint8_t]: value object  - Raw SNMP object uint64_t aligned.
 *
 * Errors is a list of SnmpErrors.  Errors during collection do not throw unless there is an issue
 * with the parameters of this function.  This is to reduce the need to acquire the GIL and to
 * promote multithreading.
 */
std::tuple<std::vector<py::array_t<uint8_t>>, std::vector<SnmpError>>
collect(
    PduType pdu_type,
    std::vector<Host> hosts,
    std::vector<NullVarBind> var_binds,
    std::optional<SnmpConfig> config,
    std::optional<uint64_t> max_active_sessions
);

}

#endif
