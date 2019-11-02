snmp-fetch
==========

|Version badge| |Python version badge| |PyPI format badge| |Build badge| |Coverage badge|

.. |Version badge| image:: https://img.shields.io/pypi/v/snmp-fetch
   :target: https://pypi.org/project/snmp-fetch/

.. |Python version badge| image:: https://img.shields.io/pypi/pyversions/snmp-fetch
   :alt: PyPI - Python Version
   :target: https://pypi.org/project/snmp-fetch/
  
.. |PyPI format badge| image:: https://img.shields.io/pypi/format/snmp-fetch
   :alt: PyPI - Format
   :target: https://pypi.org/project/snmp-fetch/

.. |Build badge| image:: https://travis-ci.org/higherorderfunctor/snmp-fetch.svg?branch=master
   :target: https://travis-ci.org/higherorderfunctor/snmp-fetch

.. |Coverage badge| image:: https://coveralls.io/repos/github/higherorderfunctor/snmp-fetch/badge.svg
   :target: https://coveralls.io/github/higherorderfunctor/snmp-fetch

An opinionated python3.7 SNMPv2 library designed for rapid database ingestion.

Prerequisites
"""""""""""""

Snmp-fetch is built for python 3.7 and c++17.  Building is currently only tested on gcc 8 and each release is only tested against the latest version of each prerequisite dependency.  The following prerequisites must be installed before adding snmp-fetch to your project.

net-snmp
''''''''

A recent version of net-snmp is required; testing has only been performed against net-snmp 5.8.

.. code:: console

   # perl bindings may be needed on RPM based systems
   sudo yum install perl-devel

   # compile and install net-snmp
   wget https://sourceforge.net/projects/net-snmp/files/net-snmp/5.8/net-snmp-5.8.tar.gz/download -O net-snmp.tar.gz
   tar xzfv net-snmp.tar.gz
   cd net-snmp-5.8
   ./configure --enable-ipv6 --with-defaults
   make
   sudo make install
   cd .. && rm -rf net-snmp*
   sudo ldconfig -v

boost (headers only)
''''''''''''''''''''

Boost is a popular C++ library to reduce boilerplate.  Snmp-fetch makes use of some of the header only libraries.

.. code:: console

   wget https://dl.bintray.com/boostorg/release/1.71.0/source/boost_1_71_0.tar.gz
   tar xzfv boost_1_71_0.tar.gz
   sudo mv boost_1_71_0/boost /usr/local/include/
   rm -rf boost_1_71_0*

pybind11
''''''''

Pybind11 is a C++ wrapper around the Python C API to reduce boilerplate.  This is a header only library, but the test script will attempt to build a binary.

.. code:: console

   # install pytest in the user space for the test build
   pip3.7 install --user pytest

   # install cmake
   wget https://github.com/Kitware/CMake/releases/download/v3.15.4/cmake-3.15.4-Linux-x86_64.sh
   chmod a+x cmake-3.15.4-Linux-x86_64.sh
   sudo ./cmake-3.15.4-Linux-x86_64.sh \
     --prefix=/usr/local/ \
     --exclude-subdir \
     --skip-license
   rm cmake-3.15.4-Linux-x86_64.sh

   # test and install pybind11
   wget https://github.com/pybind/pybind11/archive/v2.4.3.tar.gz -O pybind11.tar.gz
   tar -xvf pybind11.tar.gz
   cd pybind11-2.4.3
   mkdir -p build && cd build
   cmake .. -DPYBIND11_CPP_STANDARD=-std=c++17 -DDOWNLOAD_CATCH=1
   make check -j 4
   sudo make install
   cd ../../
   rm -rf pybind11*

Installation
""""""""""""

.. code:: console

   # poetry
   poetry add snmp-fetch --no-dev
   # pip
   pip install snmp-fetch

Examples
""""""""

The examples use jupyter and the dependencies can be installed using the following:

.. code:: console

   git clone https://github.com/higherorderfunctor/snmp-fetch.git
   cd snmp_fetch
   virtualenv -p python3.7 ENV
   source ENV/bin/activate
   poetry install
   poetry install -E notebooks
   jupyter lab

Development
"""""""""""

`Poetry <https://poetry.eustace.io/>`_ is required for the development of snmp-fetch.

.. code:: console

   # git submodule update --init

   # add the testing framework
   wget -P tests/capi https://raw.githubusercontent.com/catchorg/Catch2/master/single_include/catch2/catch.hpp

   # clone the repository
   git clone https://github.com/higherorderfunctor/snmp-fetch.git
   cd snmp-fetch

   # setup the virtual environment - mypy uses symbolic links in the 'stubs' directory to
   # expose packages that play nicely with the static type checker
   virtualenv -p python3.7 ENV
   source ENV/bin/activate
   poetry install

   # python linting
   poetry run isort -rc --atomic .
   poetry run pylint snmp_fetch tests
   poetry run flake8 snmp_fetch tests
   poetry run mypy -p snmp_fetch -p tests
   poetry run bandit -r snmp_fetch

   # C++ linting
   # TODO

   # python testing
   poetry run pytest -v --hypothesis-show-statistics tests
   # fail fast testing
   poetry run pytest -x --ff tests

   # C++ testing (GCC) 
   wget -P tests/capi https://raw.githubusercontent.com/catchorg/Catch2/master/single_include/catch2/catch.hpp
   g++ -std=c++17 `python-config --cflags` -O0 \
     src/capi/*.cpp \
     tests/capi/test_capi.cpp \
     -o test_capi \
     -L"$(python-config --prefix)/lib" \
     `python-config --ldflags` \
     `net-snmp-config --libs`
   LD_LIBRARY_PATH="$(python-config --prefix)/lib" ./test_capi

   # C++ testing (CLANG)
   # TODO


Known Limitations
"""""""""""""""""
- Changes between v0.1.x versions may introduce breaking changes.

- The library only supports SNMPv2 at this time.

- `BULKGET_REQUEST` and `NEXT_REQUEST` will always perform a walk.

- Walks will always end if the root of the OID runs past the requested OID.

- Duplicate objects on the same host/request will be silently discarded.

  - This includes the initial request; walks must be performed on an OID prior to the first desired.

- NO_SUCH_INSTANCE, NO_SUCH_OBJECT, and END_OF_MIB_VIEW response variable bindings are exposed as errors for handling by the client.
