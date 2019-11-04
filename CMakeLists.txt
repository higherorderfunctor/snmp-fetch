cmake_minimum_required(VERSION 3.12.4)
project(snmp_fetch)

include(ExternalProject)
include(ProcessorCount)

find_package(OpenSSL REQUIRED)

set(CMAKE_CXX_STANDARD 17)
set(PYBIND11_CPP_STANDARD -std=c++17)

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

# get and install boost
ExternalProject_Add(boost
  GIT_REPOSITORY https://github.com/boostorg/boost.git
  GIT_TAG boost-1.71.0
  GIT_SHALLOW 1
  GIT_CONFIG ${GIT_CONFIG}
  CONFIGURE_COMMAND ./bootstrap.sh --prefix=${CMAKE_BINARY_DIR}
  BUILD_COMMAND ./b2 headers
  INSTALL_COMMAND cmake -E copy_directory boost ${CMAKE_BINARY_DIR}/include/boost
  BUILD_IN_SOURCE 1
  UPDATE_COMMAND ""
)

# add pybind11 headers
add_subdirectory(lib/pybind11)

# define the net-snmp library
add_library(libnetsnmp STATIC IMPORTED)
set_target_properties(libnetsnmp PROPERTIES
	POSITION_INDEPENDENT_CODE ON
	IMPORTED_LOCATION ${CMAKE_BINARY_DIR}/lib/libnetsnmp${CMAKE_STATIC_LIBRARY_SUFFIX}
)

# define the python module
pybind11_add_module(capi
  src/capi/capimodule.cpp
  src/capi/asyncio.cpp
  src/capi/debug.cpp
  src/capi/results.cpp
  src/capi/session.cpp
  src/capi/types.cpp
  src/capi/utils.cpp
)

# add the net-snmp library to the python module
target_link_libraries(capi
	PRIVATE libnetsnmp
	PUBLIC OpenSSL::Crypto
)

# define dependencies
add_dependencies(capi
  netsnmp
  boost
)

if(BUILD_TESTING)

  # testing
  enable_testing()

  # add Catch2 for testing
  set(CATCH_SOURCE_DIR ${PROJECT_SOURCE_DIR}/lib/Catch2)
  add_subdirectory(${CATCH_SOURCE_DIR})
  include_directories(${CATCH_SOURCE_DIR}/single_include/catch2)

  # define the test application
  add_executable(test_capi EXCLUDE_FROM_ALL
    tests/capi/test_capi.cpp
    src/capi/capimodule.cpp
    src/capi/asyncio.cpp
    src/capi/debug.cpp
    src/capi/results.cpp
    src/capi/session.cpp
    src/capi/types.cpp
    src/capi/utils.cpp
  )

  # add compiler options
  target_compile_options(test_capi PRIVATE -O0 -fprofile-arcs -ftest-coverage)

  # define test dependencies
  add_dependencies(test_capi
    netsnmp
    boost
  )

  # add test libraries to the test application
  target_link_libraries(test_capi
    PRIVATE Catch2::Catch2 pybind11::embed libnetsnmp gcov
	  PUBLIC OpenSSL::Crypto
  )

  # add the test cases to CTest
  include(CTest)
  include(${CATCH_SOURCE_DIR}/contrib/Catch.cmake)
  catch_discover_tests(test_capi)

endif()
