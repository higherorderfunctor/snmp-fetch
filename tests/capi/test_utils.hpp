#include "catch.hpp"

#include "../../src/capi/utils.hpp"

TEST_CASE( "Test utility methods", "[utils]" ) {

  std::vector<uint64_t> oid = { 0, 1, 2, 3, 4 };

  REQUIRE( snmp_fetch::oid_to_string(oid) == ".0.1.2.3.4" );

}
