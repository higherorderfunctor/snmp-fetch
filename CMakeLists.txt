cmake_minimum_required(VERSION 3.15.4)
project(snmp_fetch)

include(ExternalProject)

set(PYBIND11_CPP_STANDARD -std=c++17)

ExternalProject_Add(
  netsnmp
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/lib/net-snmp
  CONFIGURE_COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/lib/net-snmp/configure --prefix=${CMAKE_CURRENT_SOURCE_DIR}/lib/net-snmp --with-defaults --enable-ipv6 --disable-agent --disable-mibs --disable-embedded-perl --without-perl-modules
  PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/lib/net-snmp
  BUILD_COMMAND make
  BUILD_IN_SOURCE 1
)

add_subdirectory(lib/pybind11)

pybind11_add_module(
  capi
  src/capi/capimodule.cpp
  src/capi/asyncio.cpp
  src/capi/debug.cpp
  src/capi/results.cpp
  src/capi/session.cpp
  src/capi/types.cpp
  src/capi/utils.cpp
)
