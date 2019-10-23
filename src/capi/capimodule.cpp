/**
 *  capimodule.cpp - Main entry point for the python C++ extension.
 */

#include "capimodule.hpp"

namespace py = pybind11;

namespace snmp_fetch {

/**
 *  as_pyarray
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
 *  fetch
 */
std::tuple<std::vector<py::array_t<uint8_t>>, std::vector<SnmpError>>
fetch(
    PDU_TYPE pdu_type,
    std::vector<host_t> hosts,
    std::vector<var_bind_t> var_binds,
    SnmpConfig config
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
  py::enum_<PDU_TYPE>(m, "PduType")
    .value("GET_REQUEST", GET_REQUEST)
    .value("NEXT_REQUEST", NEXT_REQUEST)
    .value("BULKGET_REQUEST", BULKGET_REQUEST)
    .export_values();

  // expose the SnmpConfig class to python
  py::class_<SnmpConfig>(m, "SnmpConfig")
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
    // allow direct access to all the SnmpConfig properties from python
    .def_readwrite("retries", &SnmpConfig::retries)
    .def_readwrite("timeout", &SnmpConfig::timeout)
    .def_readwrite("max_active_sessions", &SnmpConfig::max_active_sessions)
    .def_readwrite("max_var_binds_per_pdu", &SnmpConfig::max_var_binds_per_pdu)
    .def_readwrite("max_bulk_repetitions",  &SnmpConfig::max_bulk_repetitions)
    // comparison operator
    .def("__eq__", [](SnmpConfig &a, const SnmpConfig &b) {
        return a == b;
    }, py::is_operator())
    // attr style printing of the SnmpConfig object
    .def("__str__", [](SnmpConfig &config) { return config.to_string(); })
    // attr style representation of the SnmpConfig object
    .def("__repr__", [](SnmpConfig &config) { return config.to_string(); })
    // pickle support
    .def(py::pickle(
      [](const SnmpConfig &snmp_config) {
        return py::make_tuple(
          snmp_config.retries,
          snmp_config.timeout,
          snmp_config.max_active_sessions,
          snmp_config.max_var_binds_per_pdu,
          snmp_config.max_bulk_repetitions
        );
      },
      [](py::tuple t) {
        return SnmpConfig(
            t[0].cast<ssize_t>(),
            t[1].cast<ssize_t>(),
            t[2].cast<size_t>(),
            t[3].cast<size_t>(),
            t[4].cast<size_t>()
        );
      }
    ));

  // expose error types to python
  py::enum_<SNMP_ERROR_TYPE>(m, "SnmpErrorType")
    .value("SESSION_ERROR", SESSION_ERROR)
    .value("CREATE_REQUEST_PDU_ERROR", CREATE_REQUEST_PDU_ERROR)
    .value("SEND_ERROR", SEND_ERROR)
    .value("BAD_RESPONSE_PDU_ERROR", BAD_RESPONSE_PDU_ERROR)
    .value("TIMEOUT_ERROR", TIMEOUT_ERROR)
    .value("ASYNC_PROBE_ERROR", ASYNC_PROBE_ERROR)
    .value("TRANSPORT_DISCONNECT_ERROR", TRANSPORT_DISCONNECT_ERROR)
    .value("CREATE_RESPONSE_PDU_ERROR", CREATE_RESPONSE_PDU_ERROR)
    .value("VALUE_WARNING", VALUE_WARNING)
    .export_values();

  // expose the SnmpError class to python
  py::class_<SnmpError>(m, "SnmpError")
    // init function with defaults
    .def(
        py::init<
          SNMP_ERROR_TYPE,
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
        py::arg("err_stat") = std::nullopt,
        py::arg("err_index") = std::nullopt,
        py::arg("err_oid") = std::nullopt,
        py::arg("message") = std::nullopt
    )
    // allow direct access to all the SnmpError properties from python
    .def_readwrite("type", &SnmpError::type)
    .def_readwrite("host", &SnmpError::host)
    .def_readwrite("sys_errno", &SnmpError::sys_errno)
    .def_readwrite("snmp_errno", &SnmpError::snmp_errno)
    .def_readwrite("err_stat", &SnmpError::err_stat)
    .def_readwrite("err_index", &SnmpError::err_index)
    .def_readwrite("err_oid", &SnmpError::err_oid)
    .def_readwrite("message",  &SnmpError::message)
    // comparison operator
    .def("__eq__", [](SnmpError &a, const SnmpError &b) {
        return a == b;
    }, py::is_operator())
    // attr style printing of the SnmpError object
    .def("__str__", [](SnmpError &error) { return error.to_string(); })
    // attr style representation of the SnmpError object
    .def("__repr__", [](SnmpError &error) { return error.to_string(); })
    // pickle support
    .def(py::pickle(
      [](const SnmpError &snmp_error) {
        return py::make_tuple(
          snmp_error.type,
          snmp_error.host,
          snmp_error.sys_errno,
          snmp_error.snmp_errno,
          snmp_error.err_stat,
          snmp_error.err_index,
          snmp_error.err_oid,
          snmp_error.message
        );
      },
      [](py::tuple t) {
        return SnmpError(
            t[0].cast<SNMP_ERROR_TYPE>(),
            t[1].cast<host_t>(),
            t[2].cast<std::optional<int64_t>>(),
            t[3].cast<std::optional<int64_t>>(),
            t[4].cast<std::optional<int64_t>>(),
            t[5].cast<std::optional<int64_t>>(),
            t[6].cast<std::optional<oid_t>>(),
            t[7].cast<std::optional<std::string>>()
          );
      }
    ));

  // module method for accessing the fetch endpoint
  m.def(
      "fetch", &fetch, "Fetch SNMP objects from remote devices",
      py::arg("pdu_type"),
      py::arg("hosts"),
      py::arg("var_binds"),
      py::arg("config") = SnmpConfig()
  );

}

}
