/**
 *  capimodule.cpp - Main entry point for the python C++ extension.
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

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
as_pyarray(Sequence& seq) {
  Sequence* seq_ptr = new Sequence(std::move(seq));
  auto capsule = py::capsule(seq_ptr, [](void* p) {
    delete reinterpret_cast<Sequence*>(p);
  });
  return py::array(seq_ptr->size(), seq_ptr->data(), capsule);
}

/**
 *  fetch - Python interface for making an SNMP request.
 *
 *  @param pdu_type  SNMP_MSG_GET, SNMP_MSG_GETNEXT, or SNMP_MSG_GETBULK from the net-snmp
 *                   library.  These are enumerated to GET_REQUEST, GETNEXT_REQUEST, and
 *                   GETBULK_REQUEST in types.hpp, which are exposed as constants on the python
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
    Config config
) {

  /**
   *  Perform parameter validation.  Outside of this section, nothing should be thrown.
   *  Pybind11 does most of the checks via the type system conversion.
   */
  
  // check at least one host
  if (var_binds.empty())
    // raise an exception to the caller
    throw std::runtime_error("No hosts supplied");

  // check at least one var_bind
  if (var_binds.empty())
    // raise an exception to the caller
    throw std::runtime_error("No variable bindings supplied");

  /**
   *  One variable binding cannot be a subtree of another or be equal.  Each variable binding
   *  is used as the root to identify which vector to append the results into.  Subtree or equal
   *  roots would cause ambiguity in the result vector selection.
   */

  // loop through 0..n-1 var_binds as 'it'
  for (auto it = var_binds.begin(); it != std::next(var_binds.end(), -1); ++it)
    // loop through it..n var_binds as 'jt'
    for (auto jt = std::next(it, 1); jt != var_binds.end(); ++jt)
      // Check if either is a subtree of the other.  This comparison checks to the length of the
      // shortest oid.  If the result is 0, one is a subtree of the other or equal which fails the
      // check.
      if (
          not snmp_oidtree_compare(
            std::get<0>(*it).data(), std::get<0>(*it).size(),
            std::get<0>(*jt).data(), std::get<0>(*jt).size()
          )
      )
        // raise an exception to the caller
        throw std::invalid_argument(
            "Ambiguous root OIDs: (" +
            oid_to_string(std::get<0>(*it)) + ", " +
            oid_to_string(std::get<0>(*jt)) + ")"
        );

  // release the GIL - entering pure C++ code
  py::gil_scoped_release release;

  // init the results vector; stores one vector per var_bind in the request
  std::vector<std::vector<uint8_t>> results(var_binds.size(), std::vector<uint8_t>());
  // init the errors return list
  std::vector<SnmpError> errors;

  // run the IO loop
  run(pdu_type, hosts, var_binds, results, errors, config);

  // acquire the GIL - exiting pure C++ code
  py::gil_scoped_acquire acquire;

  // init the python results vector
  std::vector<py::array_t<uint8_t>> py_results;
  // wrap C++ vectors with numpy arrays
  std::transform(
      results.begin(),
      results.end(),
      std::back_inserter(py_results),
      [](std::vector<uint8_t> v) { return as_pyarray(v); }
  );

  // return the results and errors as a tuple
  return std::make_tuple(py_results, errors);

}


/**
 *  capi - Python module definition.
 */
PYBIND11_MODULE(capi, m) {
  // module doc comment
  m.doc() = "Python wrapper around snmp-fetch C++ API.";

  // expose PDU types to python
  py::enum_<PDU_TYPE>(m, "pdu_type")
    .value("GET_REQUEST", GET_REQUEST)
    .value("NEXT_REQUEST", NEXT_REQUEST)
    .value("GETBULK_REQUEST", GETBULK_REQUEST)
    .export_values();

  // expose the Config class to python
  py::class_<Config>(m, "Config")
    // init function with defaults
    .def(
        py::init<
          ssize_t,
          ssize_t,
          size_t,
          size_t,
          size_t
        >(),
        py::arg("retries") = SNMP_FETCH__DEFAULT_RETRIES,
        py::arg("timeout") = SNMP_FETCH__DEFAULT_TIMEOUT,
        py::arg("max_active_sessions") = SNMP_FETCH__DEFAULT_MAX_ACTIVE_SESSIONS,
        py::arg("max_var_binds_per_pdu") = SNMP_FETCH__DEFAULT_MAX_VAR_BINDS_PER_PDU,
        py::arg("max_bulk_repetitions") = SNMP_FETCH__DEFAULT_MAX_BULK_REPETITIONS
    )
    // allow direct access to all the Config properties from python
    .def_readwrite("retries", &Config::retries)
    .def_readwrite("timeout", &Config::timeout)
    .def_readwrite("max_active_sessions", &Config::max_active_sessions)
    .def_readwrite("max_var_binds_per_pdu", &Config::max_var_binds_per_pdu)
    .def_readwrite("max_bulk_repetitions",  &Config::max_bulk_repetitions)
    // attr style printing of the Config object
    .def("__str__", [](Config &config) { return config.to_string(); })
    // attr style representation of the Config object
    .def("__repr__", [](Config &config) { return config.to_string(); });

  // expose error types to python
  py::enum_<ERROR_TYPE>(m, "error_type")
    .value("SESSION_ERROR", SESSION_ERROR)
    .value("CREATE_REQUEST_PDU_ERROR", CREATE_REQUEST_PDU_ERROR)
    .value("SEND_ERROR", SEND_ERROR)
    .value("BAD_RESPONSE_PDU_ERROR", BAD_RESPONSE_PDU_ERROR)
    .value("TIMEOUT_ERROR", TIMEOUT_ERROR)
    .value("ASYNC_PROBE_ERROR", ASYNC_PROBE_ERROR)
    .value("TRANSPORT_DISCONNECT_ERROR", TRANSPORT_DISCONNECT_ERROR)
    .value("CREATE_RESPONSE_PDU_ERROR", CREATE_RESPONSE_PDU_ERROR)
    .export_values();

  // expose the SnmpError class to python
  py::class_<SnmpError>(m, "SnmpError")
    // init function with defaults
    .def(
        py::init<
          ERROR_TYPE,
          host_t,
          std::optional<int64_t>,
          std::optional<int64_t>,
          std::optional<int64_t>,
          std::optional<int64_t>,
          std::optional<oid_t>,
          std::optional<std::string>
        >(),
        py::arg("type"),
        py::arg("host"),
        py::arg("sys_errno") = std::nullopt,
        py::arg("snmp_error") = std::nullopt,
        py::arg("errstat") = std::nullopt,
        py::arg("errindex") = std::nullopt,
        py::arg("erroid") = std::nullopt,
        py::arg("message") = std::nullopt
    )
    // allow direct access to all the SnmpError properties from python
    .def_readwrite("type", &SnmpError::type)
    .def_readwrite("host", &SnmpError::host)
    .def_readwrite("sys_errno", &SnmpError::sys_errno)
    .def_readwrite("snmp_errno", &SnmpError::snmp_errno)
    .def_readwrite("errstat", &SnmpError::errstat)
    .def_readwrite("errindex", &SnmpError::errindex)
    .def_readwrite("erroid", &SnmpError::erroid)
    .def_readwrite("message",  &SnmpError::message)
    // attr style printing of the SnmpError object
    .def("__str__", [](SnmpError &error) { return error.to_string(); })
    // attr style representation of the SnmpError object
    .def("__repr__", [](SnmpError &error) { return error.to_string(); });

  // module method for accessing the fetch endpoint
  m.def(
      "fetch", &fetch, "Fetch SNMP objects from remote devices",
      py::arg("pdu_type"),
      py::arg("hosts"),
      py::arg("var_binds"),
      py::arg("config") = Config()
  );

}

}
