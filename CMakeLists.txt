cmake_minimum_required(VERSION 3.12.4)
project(snmp_fetch)

include(ExternalProject)
include(ProcessorCount)

find_package(OpenSSL REQUIRED)

set(CMAKE_CXX_STANDARD 17)
set(PYBIND11_CPP_STANDARD -std=c++17)

include_directories(lib/boost)
include_directories(lib/soq/src/libsoq)
include_directories(${CMAKE_BINARY_DIR}/include)

if(DEFINED ENV{NETFRAME_DEBUG})
  message(STATUS "Netframe debug mode enabled")
  add_definitions(-DDEBUG)
  set(CMAKE_BUILD_TYPE Debug)
  message("Build type is " ${CMAKE_BUILD_TYPE})
endif()

# increase install speed with parallel builds
ProcessorCount(N)
if(NOT N EQUAL 0)
  set(GIT_CONFIG submodule.fetchJobs=${N})
  set(MAKEFLAGS -j${N})
endif()

# get, build, and install net-snmp
ExternalProject_Add(netsnmp
  GIT_REPOSITORY https://git.code.sf.net/p/net-snmp/code
  GIT_TAG v5.8
  GIT_SHALLOW 1
  GIT_CONFIG ${GIT_CONFIG}
  CMAKE_ARGS
    -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
  CONFIGURE_COMMAND ./configure --prefix=${CMAKE_BINARY_DIR} --with-defaults --enable-ipv6 --disable-agent --disable-applications --disable-manuals --disable-scripts --disable-mibs --disable-mib-loading --disable-debugging --disable-embedded-perl --without-perl-modules --enable-static --disable-shared --with-pic --with-ldflags=-Bstatic
  BUILD_COMMAND ${CMAKE_MAKE_PROGRAM} snmplib
  INSTALL_COMMAND ${CMAKE_MAKE_PROGRAM} installlocalheaders && cd snmplib && ${CMAKE_MAKE_PROGRAM} install
  BUILD_IN_SOURCE 1
  UPDATE_COMMAND ""
)

# add pybind11
file(GLOB PYBIND11_DIR_FILES lib/pybind11/)
list(LENGTH PYBIND11_DIR_FILES PYBIND11_EMPTY)
# force clone if the directory is empty (happens when this package is installed directly from git via  a package manager)
if(PYBIND11_EMPTY EQUAL 0)
  file(REMOVE_RECURSE lib/pybind11)
  execute_process(
    COMMAND git submodule update --init lib/pybind11
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
  )
endif()
add_subdirectory(lib/pybind11)

# define net-snmp library
add_library(libnetsnmp STATIC IMPORTED)
set_target_properties(libnetsnmp PROPERTIES
  POSITION_INDEPENDENT_CODE ON
  IMPORTED_LOCATION ${CMAKE_BINARY_DIR}/lib/libnetsnmp${CMAKE_STATIC_LIBRARY_SUFFIX}
)

# define python module
pybind11_add_module(api
  snmp_fetch/snmp/api/module.cpp
  snmp_fetch/snmp/api/asyncio.cpp
  snmp_fetch/snmp/api/results.cpp
  snmp_fetch/snmp/api/session.cpp
  snmp_fetch/snmp/api/types.cpp
  snmp_fetch/snmp/api/utils.cpp
  lib/soq/src/libsoq/debug.c
  lib/soq/src/libsoq/kludge.c
  lib/soq/src/libsoq/stderr.c
)

SET(LIBS libnetsnmp OpenSSL::Crypto)

if(DEFINED ENV{NETFRAME_COVERAGE})
  message(STATUS "Netframe overage reporting enabled")
  target_compile_options(api
    PRIVATE -O0 -ftest-coverage -fprofile-arcs
  )
  LIST(APPEND LIBS gcov)
endif()

# add the net-snmp library to the python module
target_link_libraries(api
  PRIVATE ${LIBS}
)

# define dependencies
add_dependencies(api
  netsnmp
)
