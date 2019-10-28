#include "catch.hpp"
#include "../../src/capi/capimodule.hpp"

namespace py = pybind11;

using namespace snmp_fetch;

TEST_CASE( "Test timeout", "[fetch]" ) {

  std::vector<host_t> hosts = {
    std::make_tuple(0, "localhost", "public")
  };
  std::vector<var_bind_t> var_binds = {
    std::make_tuple<oid_t, var_bind_size_t>(
      { 1 }, std::make_tuple(0, 0)
    )
  };
  SnmpConfig config;

  auto [results, errors] = fetch(GET, hosts, var_binds, config);

  REQUIRE( results.size() == 1 );
  REQUIRE( results[0].size() == 0 );
  REQUIRE( errors.size() == 1 );
  REQUIRE( errors[0].type == TIMEOUT_ERROR );

}
