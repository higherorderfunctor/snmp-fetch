/**
 * Main entry point implementation for the python C++ extension.
 */

#include "module.hpp"

#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include "utils.hpp"

namespace py = pybind11;

namespace netframe::api {

template <typename Sequence>
inline py::array_t<typename Sequence::value_type>
as_pyarray(Sequence& seq) {
  Sequence* seq_ptr = new Sequence(std::move(seq));
  auto capsule = py::capsule(seq_ptr, [](void* p) {
    delete reinterpret_cast<Sequence*>(p);
  });
  return py::array(seq_ptr->size(), seq_ptr->data(), capsule);
}

std::tuple<std::vector<py::array_t<uint8_t>>, std::vector<SnmpError>>
collect(
    PduType pdu_type,
    std::vector<Host> hosts,
    std::vector<NullVarBind> var_binds,
    std::optional<SnmpConfig> config,
    std::optional<uint64_t> max_active_sessions
) {

  // Perform parameter validation.  Outside of this section, nothing should be thrown.
  // Pybind11 does most of the checks via the type system conversion.
  if (hosts.empty())
    throw std::runtime_error("No hosts supplied");
 
  if (var_binds.empty())
    throw std::runtime_error("No variable bindings supplied");

  // One variable binding cannot be a subtree of another or be equal.  Each variable binding
  // is used as the root to identify which vector to append the results into.  Subtree or equal
  // roots would cause ambiguity in the result vector selection.

  // loop through 0..n-1 var_binds as 'it'
  for (auto it = var_binds.begin(); it != std::next(var_binds.end(), -1); ++it)
    // loop through it..n var_binds as 'jt'
    for (auto jt = std::next(it, 1); jt != var_binds.end(); ++jt)
      // Check if either is a subtree of the other.  This comparison checks to the length of the
      // shortest oid.  If the result is 0, one is a subtree of the other or equal which fails the
      // check.
      if (!snmp_oidtree_compare(
            it->oid.data(), it->oid.size(),
            jt->oid.data(), jt->oid.size()
      ))
         // raise an exception to the caller
         throw std::invalid_argument(
             "Ambiguous root OIDs: (" + oid_to_string(it->oid) + ", " +
             oid_to_string(jt->oid) + ")"
         );
 
  // release the GIL - entering pure C++ code
  py::gil_scoped_release release;

  std::vector<std::vector<uint8_t>> results(var_binds.size(), std::vector<uint8_t>());
  std::vector<SnmpError> errors;

  // run the IO loop
  // run(pdu_type, hosts, var_binds, results, errors, config);

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
 

PYBIND11_MODULE(api, m) {
  m.doc() = "Python wrapper around netframe::api's C++ API.";

  py::enum_<PduType>(m, "PduType")
    .value("GET", GET)
    .value("NEXT", NEXT)
    .value("BULKGET", BULKGET)
    .export_values();

  py::class_<SnmpConfig>(m, "SnmpConfig")
    .def(
        py::init<
          ssize_t,
          ssize_t,
          size_t,
          size_t
        >(),
        py::arg("retries") = DEFAULT_RETRIES,
        py::arg("timeout") = DEFAULT_TIMEOUT,
        py::arg("var_binds_per_pdu") = DEFAULT_VAR_BINDS_PER_PDU,
        py::arg("bulk_repetitions") = DEFAULT_BULK_REPETITIONS
    )
    .def_readwrite("retries", &SnmpConfig::retries)
    .def_readwrite("timeout", &SnmpConfig::timeout)
    .def_readwrite("var_binds_per_pdu", &SnmpConfig::var_binds_per_pdu)
    .def_readwrite("bulk_repetitions",  &SnmpConfig::bulk_repetitions)
    .def("__eq__", [](SnmpConfig &a, const SnmpConfig &b) {
        return a == b;
    }, py::is_operator())
    .def("__str__", [](SnmpConfig &config) { return config.to_string(); })
    .def("__repr__", [](SnmpConfig &config) { return config.to_string(); })
    .def(py::pickle(
      [](const SnmpConfig &config) {
        return py::make_tuple(
          config.retries,
          config.timeout,
          config.var_binds_per_pdu,
          config.bulk_repetitions
        );
      },
      [](py::tuple t) {
        return (SnmpConfig) {
            t[0].cast<ssize_t>(),
            t[1].cast<ssize_t>(),
            t[2].cast<size_t>(),
            t[3].cast<size_t>()
          };
      }
    ));

  py::enum_<SnmpErrorType>(m, "SnmpErrorType")
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

//   // expose the SnmpError class to python
//   py::class_<SnmpError>(m, "SnmpError")
//     // init function with defaults
//     .def(
//         py::init<
//           SNMP_ERROR_TYPE,
//           host_t,
//           std::optional<int64_t>,
//           std::optional<int64_t>,
//           std::optional<int64_t>,
//           std::optional<int64_t>,
//           std::optional<oid_t>,
//           std::optional<std::string>
//         >(),
//         py::arg("type"),
//         py::arg("host"),
//         py::arg("sys_errno") = std::nullopt,
//         py::arg("snmp_error") = std::nullopt,
//         py::arg("err_stat") = std::nullopt,
//         py::arg("err_index") = std::nullopt,
//         py::arg("err_oid") = std::nullopt,
//         py::arg("message") = std::nullopt
//     )
//     // allow direct access to all the SnmpError properties from python
//     .def_readwrite("type", &SnmpError::type)
//     .def_readwrite("host", &SnmpError::host)
//     .def_readwrite("sys_errno", &SnmpError::sys_errno)
//     .def_readwrite("snmp_errno", &SnmpError::snmp_errno)
//     .def_readwrite("err_stat", &SnmpError::err_stat)
//     .def_readwrite("err_index", &SnmpError::err_index)
//     .def_readwrite("err_oid", &SnmpError::err_oid)
//     .def_readwrite("message",  &SnmpError::message)
//     // comparison operator
//     .def("__eq__", [](SnmpError &a, const SnmpError &b) {
//         return a == b;
//     }, py::is_operator())
//     // attr style printing of the SnmpError object
//     .def("__str__", [](SnmpError &error) { return error.to_string(); })
//     // attr style representation of the SnmpError object
//     .def("__repr__", [](SnmpError &error) { return error.to_string(); })
//     // pickle support
//     .def(py::pickle(
//       [](const SnmpError &snmp_error) {
//         return py::make_tuple(
//           snmp_error.type,
//           snmp_error.host,
//           snmp_error.sys_errno,
//           snmp_error.snmp_errno,
//           snmp_error.err_stat,
//           snmp_error.err_index,
//           snmp_error.err_oid,
//           snmp_error.message
//         );
//       },
//       [](py::tuple t) {
//         return SnmpError(
//             t[0].cast<SNMP_ERROR_TYPE>(),
//             t[1].cast<host_t>(),
//             t[2].cast<std::optional<int64_t>>(),
//             t[3].cast<std::optional<int64_t>>(),
//             t[4].cast<std::optional<int64_t>>(),
//             t[5].cast<std::optional<int64_t>>(),
//             t[6].cast<std::optional<oid_t>>(),
//             t[7].cast<std::optional<std::string>>()
//           );
//       }
//     ));
// 

  m.def(
      "collect", &collect, "Collect SNMP objects from remote devices",
      py::arg("pdu_type"),
      py::arg("hosts"),
      py::arg("var_binds"),
      py::arg("config") = std::nullopt,
      py::arg("max_active_sessions") = std::nullopt
  );

}

}
