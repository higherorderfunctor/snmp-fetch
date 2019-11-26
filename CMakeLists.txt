cmake_minimum_required(VERSION 3.12.4)
project(snmp_fetch)

include(ExternalProject)
include(ProcessorCount)

find_package(OpenSSL REQUIRED)

set(CMAKE_CXX_STANDARD 17)
set(PYBIND11_CPP_STANDARD -std=c++17)

include_directories(lib/boost)
include_directories(${CMAKE_BINARY_DIR}/include)

# increase install speed with parallel builds
ProcessorCount(N)
if(NOT N EQUAL 0)
  set(GIT_CONFIG submodule.fetchJobs=${N})
  set(MAKEFLAGS -j${N})
  set(CTEST_BUILD_FLAGS -j${N})
  set(ctest_test_args ${ctest_test_args} PARALLEL_LEVEL ${N})
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
  snmp_fetch/api/module.cpp
  #snmp_fetch/api/asyncio.cpp
  #snmp_fetch/api/results.cpp
  #snmp_fetch/api/session.cpp
  snmp_fetch/api/types.cpp
  snmp_fetch/api/utils.cpp
)

# add the net-snmp library to the python module
target_link_libraries(api
    PRIVATE libnetsnmp OpenSSL::Crypto
)

# define dependencies
add_dependencies(api
  netsnmp
)

if(BUILD_TESTING)

  enable_testing()

  # add Catch2 for testing
  set(CATCH_SOURCE_DIR ${PROJECT_SOURCE_DIR}/lib/Catch2)
  add_subdirectory(${CATCH_SOURCE_DIR})
  include_directories(${CATCH_SOURCE_DIR}/single_include/catch2)

  # define the test application
  add_executable(test_api EXCLUDE_FROM_ALL
    tests/api/test_api.cpp
    snmp_fetch/api/module.cpp
    # snmp_fetch/api/asyncio.cpp
    # snmp_fetch/api/results.cpp
    # snmp_fetch/api/session.cpp
    snmp_fetch/api/types.cpp
    snmp_fetch/api/utils.cpp
  )

  # add compiler options
  target_compile_options(test_api PRIVATE -O0 -fprofile-arcs -ftest-coverage)

  # define test dependencies
  add_dependencies(test_api
    netsnmp
  )

  # add test libraries to the test application
  target_link_libraries(test_api
    PRIVATE Catch2::Catch2 pybind11::embed libnetsnmp gcov OpenSSL::Crypto
  )

  # add test cases to CTest
  include(CTest)
  include(${CATCH_SOURCE_DIR}/contrib/Catch.cmake)
  catch_discover_tests(test_api)

endif()
