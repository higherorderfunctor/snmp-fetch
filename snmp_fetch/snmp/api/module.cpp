/**
 * Main entry point implementation for the netframe::snmp::api C++ extension.
 */

#include "module.hpp"

#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include "utils.hpp"

namespace py = pybind11;

namespace netframe::snmp::api {

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
snmp(
    PduType pdu_type,
    std::vector<Host> hosts,
    std::vector<NullVarBind> var_binds,
    std::optional<Config> config,
    uint64_t max_active_sessions
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

  m.doc() = "Python wrapper around netframe's C++ SNMP extension.";

  py::enum_<PduType>(m, "PduType")
    .value("GET", GET)
    .value("NEXT", NEXT)
    .value("BULKGET", BULKGET)
    .export_values();

  py::class_<NullVarBind>(m, "NullVarBind")
    .def(
        py::init<
          ObjectIdentity,
          uint64_t,
          uint64_t
        >(),
        py::arg("oid"),
        py::arg("oid_size"),
        py::arg("value_size")
    )
    .def_readwrite("oid", &NullVarBind::oid)
    .def_readwrite("value_size", &NullVarBind::oid_size)
    .def_readwrite("oid_size", &NullVarBind::value_size)
    .def("__eq__", [](NullVarBind &a, const NullVarBind &b) {
        return a == b;
    }, py::is_operator())
    .def("__str__", [](NullVarBind &var_bind) { return var_bind.to_string(); })
    .def("__repr__", [](NullVarBind &var_bind) { return var_bind.to_string(); })
    .def(py::pickle(
      [](const NullVarBind &var_bind) {
        return py::make_tuple(
          var_bind.oid,
          var_bind.oid_size,
          var_bind.value_size
        );
      },
      [](py::tuple t) {
        return (NullVarBind) {
            t[0].cast<ObjectIdentity>(),
            t[1].cast<uint64_t>(),
            t[2].cast<uint64_t>(),
          };
      }
    ));

  py::class_<Config>(m, "Config")
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
    .def_readwrite("retries", &Config::retries)
    .def_readwrite("timeout", &Config::timeout)
    .def_readwrite("var_binds_per_pdu", &Config::var_binds_per_pdu)
    .def_readwrite("bulk_repetitions",  &Config::bulk_repetitions)
    .def("__eq__", [](Config &a, const Config &b) {
        return a == b;
    }, py::is_operator())
    .def("__str__", [](Config &config) { return config.to_string(); })
    .def("__repr__", [](Config &config) { return config.to_string(); })
    .def(py::pickle(
      [](const Config &config) {
        return py::make_tuple(
          config.retries,
          config.timeout,
          config.var_binds_per_pdu,
          config.bulk_repetitions
        );
      },
      [](py::tuple t) {
        return (Config) {
            t[0].cast<ssize_t>(),
            t[1].cast<ssize_t>(),
            t[2].cast<size_t>(),
            t[3].cast<size_t>()
          };
      }
    ));

  py::class_<ObjectIdentityParameter>(m, "ObjectIdentityParameter")
    .def(
        py::init<
          ObjectIdentity,
          std::optional<ObjectIdentity>
        >(),
        py::arg("start"),
        py::arg("end") = std::nullopt
    )
    .def_readwrite("start", &ObjectIdentityParameter::start)
    .def_readwrite("end", &ObjectIdentityParameter::end)
    .def("__eq__", [](ObjectIdentityParameter &a, const ObjectIdentityParameter &b) {
        return a == b;
    }, py::is_operator())
    .def("__str__", [](ObjectIdentityParameter &parameter) { return parameter.to_string(); })
    .def("__repr__", [](ObjectIdentityParameter &parameter) { return parameter.to_string(); })
    .def(py::pickle(
      [](const ObjectIdentityParameter &parameter) {
        return py::make_tuple(
          parameter.start,
          parameter.end
        );
      },
      [](py::tuple t) {
        return (ObjectIdentityParameter) {
            t[0].cast<ObjectIdentity>(),
            t[1].cast<std::optional<ObjectIdentity>>()
          };
      }
    ));

  py::enum_<Version>(m, "Version")
    .value("V2C", V2C)
    .export_values();

  py::class_<Community>(m, "Community")
    .def(
        py::init<
          uint64_t,
          Version,
          std::string
        >(),
        py::arg("index"),
        py::arg("version"),
        py::arg("string")
    )
    .def_readwrite("index", &Community::index)
    .def_readwrite("version", &Community::version)
    .def_readwrite("string", &Community::string)
    .def("__eq__", [](Community &a, const Community &b) {
        return a == b;
    }, py::is_operator())
    .def("__str__", [](Community &community) { return community.to_string(); })
    .def("__repr__", [](Community &community) { return community.to_string(); })
    .def(py::pickle(
      [](const Community &community) {
        return py::make_tuple(
          community.index,
          community.version,
          community.string
        );
      },
      [](py::tuple t) {
        return (Community) {
            t[0].cast<uint64_t>(),
            t[1].cast<Version>(),
            t[2].cast<std::string>()
          };
      }
    ));

  py::class_<Host>(m, "Host")
    .def(
        py::init<
          uint64_t,
          std::string,
          std::list<Community>,
          std::optional<std::list<ObjectIdentityParameter>>,
          std::optional<Config>
        >(),
        py::arg("index"),
        py::arg("hostname"),
        py::arg("communities"),
        py::arg("parameters"),
        py::arg("config")
    )
    .def_readwrite("index", &Host::index)
    .def_readwrite("hostname", &Host::hostname)
    .def_readwrite("communities", &Host::communities)
    .def_readwrite("parameters", &Host::parameters)
    .def_readwrite("config", &Host::config)
    .def("__eq__", [](Host &a, const Host &b) {
        return a == b;
    }, py::is_operator())
    .def("__str__", [](Host &host) { return host.to_string(); })
    .def("__repr__", [](Host &host) { return host.to_string(); })
    .def(py::pickle(
      [](const Host &host) {
        return py::make_tuple(
          host.index,
          host.hostname,
          host.communities,
          host.parameters,
          host.config
        );
      },
      [](py::tuple t) {
        return (Host) {
            t[0].cast<uint64_t>(),
            t[1].cast<std::string>(),
            t[2].cast<std::list<Community>>(),
            t[3].cast<std::optional<std::list<ObjectIdentityParameter>>>(),
            t[4].cast<std::optional<Config>>()
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
      "snmp", &snmp, "Collect SNMP objects from remote devices",
      py::arg("pdu_type"),
      py::arg("hosts"),
      py::arg("var_binds"),
      py::arg("config") = std::nullopt,
      py::arg("max_active_sessions") = DEFAULT_MAX_ACTIVE_SESSIONS
  );

}

}
