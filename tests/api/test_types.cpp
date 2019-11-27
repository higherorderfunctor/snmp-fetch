#include "catch.hpp"

#include "../../snmp_fetch/api/types.hpp"

using namespace netframe::api;

TEST_CASE( "Test NullVarBind", "[types]" ) {

  NullVarBind var_bind = {
      { 0, 1, 2, 3, 4 }, 256, 512
  };

  REQUIRE( var_bind.oid == (ObjectIdentity) { 0, 1, 2, 3, 4 } );
  REQUIRE( var_bind.oid_size == 256 );
  REQUIRE( var_bind.value_size == 512 );

  REQUIRE( var_bind.to_string() == "NullVarBind(oid='.0.1.2.3.4', oid_size=256, value_size=512)" );

  auto var_bind2 = var_bind;

  REQUIRE( var_bind == var_bind2 );

  var_bind2.oid = { 0 };
  var_bind2.oid_size = 0;
  REQUIRE( !(var_bind == var_bind2) );

  var_bind2 = var_bind;
  var_bind2.oid_size = 0;
  REQUIRE( !(var_bind == var_bind2) );

  var_bind2 = var_bind;
  var_bind2.value_size = 0;
  REQUIRE( !(var_bind == var_bind2) );

}


TEST_CASE( "Test SnmpConfig", "[types]" ) {

  SnmpConfig config = { 0, 1, 2, 3 };

  REQUIRE( config.retries == 0 );
  REQUIRE( config.timeout == 1 );
  REQUIRE( config.var_binds_per_pdu == 2 );
  REQUIRE( config.bulk_repetitions == 3 );

  REQUIRE( config.to_string() == "SnmpConfig(retries=0, timeout=1, var_binds_per_pdu=2, bulk_repetitions=3)" );

  auto config2 = config;

  REQUIRE( config == config2 );

  config2.retries = -1;
  REQUIRE( !(config == config2) );

  config2 = config;
  config2.timeout = -1;
  REQUIRE( !(config == config2) );

  config2 = config;
  config2.var_binds_per_pdu = 0;
  REQUIRE( !(config == config2) );

  config2 = config;
  config2.bulk_repetitions = 0;
  REQUIRE( !(config == config2) );

}


TEST_CASE( "Test ObjectIdentityParameter", "[types]" ) {

  ObjectIdentityParameter parameter = {
    { 0, 1, 2, 3 }, { { 4, 5, 6, 7} }
  };

  REQUIRE( parameter.start == (ObjectIdentity) { 0, 1, 2, 3 } );
  REQUIRE( parameter.end == (ObjectIdentity) { 4, 5, 6, 7} );

  REQUIRE( parameter.to_string() == "ObjectIdentityParameter(start='.0.1.2.3', end='.4.5.6.7')" );

  auto parameter2 = parameter;

  REQUIRE( parameter == parameter2 );

  parameter2.start = { 0 };
  REQUIRE( !(parameter == parameter2) );

  parameter2 = parameter;
  parameter2.end = std::nullopt;

  REQUIRE( !(parameter == parameter2) );

  REQUIRE( parameter2.to_string() == "ObjectIdentityParameter(start='.0.1.2.3', end=None)" );

}


TEST_CASE( "Test Host", "[types]" ) {

  Host host = {
    1, "2", { "3" }, { { { { 0, 1, 2, 3 }, { } } } }, { { 0, 1, 2, 3 } }
  };

  REQUIRE( host.index == 1 );
  REQUIRE( host.hostname == "2" );
  REQUIRE( host.parameters == (std::list<ObjectIdentityParameter>) { { { 0, 1, 2, 3 }, { } } } );
  REQUIRE( host.config == (SnmpConfig) { 0, 1, 2, 3 } );

  REQUIRE( host.to_string() == "Host(index=1, hostname='2', communities=['3'], parameters=[ObjectIdentityParameter(start='.0.1.2.3', end=None)], config=SnmpConfig(retries=0, timeout=1, var_binds_per_pdu=2, bulk_repetitions=3))" );

  auto host2 = host;

  REQUIRE( host == host2 );

  host2.index = 0;
  REQUIRE( !(host == host2) );

  host2 = host;
  host2.hostname = "0";
  REQUIRE( !(host == host2) );

  host2 = host;
  host2.communities = { };

  REQUIRE( !(host == host2) );

  REQUIRE( host2.to_string() == "Host(index=1, hostname='2', communities=[], parameters=[ObjectIdentityParameter(start='.0.1.2.3', end=None)], config=SnmpConfig(retries=0, timeout=1, var_binds_per_pdu=2, bulk_repetitions=3))" );

  host2.communities = { "0", "1" };

  REQUIRE( host2.to_string() == "Host(index=1, hostname='2', communities=['0', '1'], parameters=[ObjectIdentityParameter(start='.0.1.2.3', end=None)], config=SnmpConfig(retries=0, timeout=1, var_binds_per_pdu=2, bulk_repetitions=3))" );

  host2 = host;
  host2.parameters = std::nullopt;

  REQUIRE( !(host == host2) );

  REQUIRE( host2.to_string() == "Host(index=1, hostname='2', communities=['3'], parameters=None, config=SnmpConfig(retries=0, timeout=1, var_binds_per_pdu=2, bulk_repetitions=3))" );

  host2.parameters = (std::list<ObjectIdentityParameter>) { };

  REQUIRE( host2.to_string() == "Host(index=1, hostname='2', communities=['3'], parameters=None, config=SnmpConfig(retries=0, timeout=1, var_binds_per_pdu=2, bulk_repetitions=3))" );

  host2.parameters = { { { 0, 1, 2, 3 }, { } }, { { 4, 5, 6, 7 }, { } } };

  REQUIRE( host2.to_string() == "Host(index=1, hostname='2', communities=['3'], parameters=[ObjectIdentityParameter(start='.0.1.2.3', end=None), ObjectIdentityParameter(start='.4.5.6.7', end=None)], config=SnmpConfig(retries=0, timeout=1, var_binds_per_pdu=2, bulk_repetitions=3))" );

  host2 = host;
  host2.config = std::nullopt;

  REQUIRE( !(host == host2) );

  REQUIRE( host2.to_string() == "Host(index=1, hostname='2', communities=['3'], parameters=[ObjectIdentityParameter(start='.0.1.2.3', end=None)], config=None)" );

}


TEST_CASE( "Test SnmpError", "[types]" ) {

  SnmpError error = {
    SESSION_ERROR, { 1, "2", { }, { }, { } },
    3, 4, 5, 6, { { 7, 8 } }, "Test"
  };

  REQUIRE( error.type == SESSION_ERROR );
  REQUIRE( error.host == (Host) { 1, "2", { }, { }, { } } );

  REQUIRE( error.to_string() == "SnmpError(type=SESSION_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  auto error2 = error;

  REQUIRE( error == error2 );

  error2.type = CREATE_REQUEST_PDU_ERROR;

  REQUIRE( !(error == error2) );

  REQUIRE( error2.to_string() == "SnmpError(type=CREATE_REQUEST_PDU_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  error2.type = SEND_ERROR;

  REQUIRE( error2.to_string() == "SnmpError(type=SEND_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  error2.type = BAD_RESPONSE_PDU_ERROR;

  REQUIRE( error2.to_string() == "SnmpError(type=BAD_RESPONSE_PDU_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  error2.type = TIMEOUT_ERROR;

  REQUIRE( error2.to_string() == "SnmpError(type=TIMEOUT_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  error2.type = ASYNC_PROBE_ERROR;

  REQUIRE( error2.to_string() == "SnmpError(type=ASYNC_PROBE_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  error2.type = TRANSPORT_DISCONNECT_ERROR;

  REQUIRE( error2.to_string() == "SnmpError(type=TRANSPORT_DISCONNECT_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  error2.type = CREATE_RESPONSE_PDU_ERROR;

  REQUIRE( error2.to_string() == "SnmpError(type=CREATE_RESPONSE_PDU_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  error2.type = VALUE_WARNING;

  REQUIRE( error2.to_string() == "SnmpError(type=VALUE_WARNING, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  error2 = error;

  error2.host = { 0, "0", { }, { }, { } };

  REQUIRE( !(error == error2) );

  REQUIRE( error2.to_string() == "SnmpError(type=SESSION_ERROR, host=Host(index=0, hostname='0', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  error2 = error;

  error2.sys_errno = std::nullopt;

  REQUIRE( !(error == error2) );

  REQUIRE( error2.to_string() == "SnmpError(type=SESSION_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=None, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  error2 = error;

  error2.snmp_errno = std::nullopt;

  REQUIRE( !(error == error2) );

  REQUIRE( error2.to_string() == "SnmpError(type=SESSION_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=None, err_stat=5, err_index=6, err_oid='.7.8', message='Test')" );

  error2 = error;

  error2.err_stat = std::nullopt;

  REQUIRE( !(error == error2) );

  REQUIRE( error2.to_string() == "SnmpError(type=SESSION_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=None, err_index=6, err_oid='.7.8', message='Test')" );

  error2 = error;

  error2.err_index = std::nullopt;

  REQUIRE( !(error == error2) );

  REQUIRE( error2.to_string() == "SnmpError(type=SESSION_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=None, err_oid='.7.8', message='Test')" );

  error2 = error;

  error2.err_oid = std::nullopt;

  REQUIRE( !(error == error2) );

  REQUIRE( error2.to_string() == "SnmpError(type=SESSION_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid=None, message='Test')" );

  error2 = error;

  error2.message = std::nullopt;

  REQUIRE( !(error == error2) );

  REQUIRE( error2.to_string() == "SnmpError(type=SESSION_ERROR, host=Host(index=1, hostname='2', communities=[], parameters=None, config=None), sys_errno=3, snmp_errno=4, err_stat=5, err_index=6, err_oid='.7.8', message=None)" );

}
