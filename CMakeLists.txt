cmake_minimum_required(VERSION 3.15.4)
project(snmp_fetch)

include(ExternalProject)

set(PYBIND11_CPP_STANDARD -std=c++17)

include_directories(${CMAKE_BINARY_DIR}/include)

# get, build, and install net-snmp
ExternalProject_Add(netsnmp
  GIT_REPOSITORY https://git.code.sf.net/p/net-snmp/code
  GIT_TAG v5.8
  GIT_SHALLOW 1
  CONFIGURE_COMMAND ./configure --prefix=${CMAKE_BINARY_DIR} --with-defaults --enable-ipv6 --disable-agent --disable-mibs --disable-mib-loading --disable-applications --disable-scripts --disable-manuals --disable-embedded-perl --without-perl-modules
  BUILD_IN_SOURCE 1
)

# get and install boost headers
ExternalProject_Add(boost
  URL https://dl.bintray.com/boostorg/release/1.71.0/source/boost_1_71_0.tar.gz
  CONFIGURE_COMMAND ""
  BUILD_COMMAND ""
  INSTALL_COMMAND ${CMAKE_COMMAND} -E copy_directory boost ${CMAKE_BINARY_DIR}/include/boost
  BUILD_IN_SOURCE 1
)

# add pybind11 headers
add_subdirectory(lib/pybind11)

# define the net-snmp library
add_library(libnetsnmp SHARED IMPORTED)
set_target_properties(libnetsnmp PROPERTIES IMPORTED_LOCATION ${CMAKE_BINARY_DIR}/lib/libnetsnmp.so)

# define the python module
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

# add the net-snmp library to the python module
target_link_libraries(capi PRIVATE libnetsnmp)

# define dependencies
add_dependencies(capi
  netsnmp
  boost
)
