#define CATCH_CONFIG_RUNNER

#include <pybind11/embed.h>
namespace py = pybind11;

#include "catch.hpp"
#include "test_utils.hpp"

int main( int argc, char* argv[] ) {

  py::scoped_interpreter guard{};

  int result = Catch::Session().run( argc, argv );

  return result;

}
