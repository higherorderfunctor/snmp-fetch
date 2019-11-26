#include "catch.hpp"

#include "../../snmp_fetch/api/utils.hpp"

TEST_CASE( "Test utility methods", "[utils]" ) {

  std::vector<uint64_t> oid = { 0, 1, 2, 3, 4 };

  REQUIRE( netframe::api::oid_to_string(oid) == ".0.1.2.3.4" );
  REQUIRE( netframe::api::oid_to_string(oid.data(), oid.size()) == ".0.1.2.3.4" );

}
