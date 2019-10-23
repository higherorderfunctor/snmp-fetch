/**
 *  capimodule.hpp - Main entry point for the python C++ extension.
 */

#ifndef SNMP_FETCH__CAPIMODULE_HPP
#define SNMP_FETCH__CAPIMODULE_HPP

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>

#include "asyncio.hpp"

namespace py = pybind11;

namespace snmp_fetch {

/**
 *  as_pyarray - Wraps a C++ sequence in a numpy array.  This object will free the underlying data
 *               when the numpy array is garbage collected.
 *
 *  @param seq Sequence to be wrapped in a numpy array.
 *  @return    Numpy array.
 */
template <typename Sequence>
inline py::array_t<typename Sequence::value_type>
as_pyarray(Sequence& seq);

/**
 *  fetch - Python interface for making an SNMP request.
 *
 *  @param pdu_type  SNMP_MSG_GET, SNMP_MSG_GETNEXT, or SNMP_MSG_GETBULK from the net-snmp
 *                   library.  These are enumerated to GET_REQUEST, GETNEXT_REQUEST, and
 *                   BULKGET_REQUEST in types.hpp, which are exposed as constants on the python
 *                   module.
 *  @param hosts     A list of tuples defining the hosts for this request.  Tuple format is
 *                   (host index, host address, community string).  Host index is an arbitrary
 *                   uint64_t used to assemble the results in python and is set by the caller.
 *  @param var_binds A list of tuples defining which snmp objects to collect.  Tuple format is
 *                   ([suboid, ...], (oid buffer size, result buffer size)).  Buffer sizes
 *                   represent the maximum number of bytes that will be stored in the return
 *                   result.  It is up to the caller to ensure the buffer size is large enough.
 *                   Behavior is undefined if the caller does not define a large enough buffer.
 *                   All buffers will be uint64_t aligned.  This can be exploited if padding is
 *                   needed on the result (e.g. a 255 byte buffer would be allocated as 256 bytes
 *                   with the last byte set to 0; this is useful for string types that need to
 *                   be null terminated).
 *  @param config    Configuration object defined in types.hpp.  This object is exposed to
 *                   python and can be directly setup by the caller.
 *  @return          A tuple of (results, errors).
 *
 *                   Results is a list of structured numpy arrays.
 *                       host index: uint64_t  - Set by caller.
 *                       oid size: uint64_t    - Number of suboids from the PDU.
 *                       oid: [uint64_t]       - Oid from the PDU.  One uint64_t per suboid up
 *                                               to uint64_t aligned buffer size supplied in
 *                                               var_binds.
 *                       object type: uint64_t - SNMP object type code from the PDU.
 *                       object size: uint64_t - Size of the SNMP object from the PDU.
 *                       object: [uint8_t]     - Raw SNMP object from the PDU.  One uint8_ up to
 *                                               uint64_t aligned buffer size supplied in
 *                                               var_binds.
 *
 *                   Errors is a list of SnmpError objects defined in types.hpp which is exposed
 *                   to python.  Errors during collection do not throw unless there is an issue
 *                   with the parameters of this function.  This is to reduce the need to acquire
 *                   the GIL and promote multithreading.
 */
std::tuple<std::vector<py::array_t<uint8_t>>, std::vector<SnmpError>>
fetch(
    PDU_TYPE pdu_type,
    std::vector<host_t> hosts,
    std::vector<var_bind_t> var_binds,
    SnmpConfig config
);

}

#endif
