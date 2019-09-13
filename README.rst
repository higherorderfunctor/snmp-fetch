snmp-fetch
==========

An opinionated SNMPv2 library built for rapid database ingestion.  This is an alpha release.


Prerequisites
"""""""""""""

Snmp-fetch is built for python 3.7 and c++17.  It is currently tested on python 3.7.4 with gcc 8.   The following prerequisites must also be installed before adding snmp-fetch to your project.

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

   wget https://dl.bintray.com/boostorg/release/1.70.0/source/boost_1_70_0.tar.gz
   tar xzfv boost_1_70_0.tar.gz
   sudo mv boost_1_70_0/boost /usr/local/include/
   rm -rf boost_1_70_0*


pybind11
''''''''

Pybind11 is a C++ wrapper around the Python C API to reduce boilerplate.  This is a header only library, but the test script will attempt to build a binary.

.. code:: console

   # install pytest in the user space for the test build
   pip3.7 install --user pytest

   # install cmake
   wget https://github.com/Kitware/CMake/releases/download/v3.15.1/cmake-3.15.1-Linux-x86_64.sh
   sudo ./cmake-3.15.1-Linux-x86_64.sh \
     --prefix=/usr/local/ \
     --exclude-subdir \
     --skip-license
   rm cmake-3.15.1-Linux-x86_64.sh

   # test and install pybind11
   git clone --depth 1 https://github.com/pybind/pybind11.git
   cd pybind11
   mkdir -p build && cd build
   cmake .. -DPYBIND11_CPP_STANDARD=-std=c++17 -DDOWNLOAD_CATCH=1
   make check -j 4
   sudo make install
   cd ../../
   rm -rf pybind11


Installation
""""""""""""

.. code:: console

   # poetry
   poetry add snmp-fetch --git https://gitlab.com/higherorderfunctor/snmp-fetch.git
   # pip
   pip install git+https://gitlab.com/higherorderfunctor/snmp-fetch.git


Development
"""""""""""

.. code:: console

   # poetry must be installed
   git clone ...
   cd snmp-fetch
   virtualenv -p python3.7 ENV
   source ENV/bin/activate
   poetry install  # if never installed
   deactivate && source ENV/bin/activate  # refresh PATH

   # fast fail testing
   pytest --hypothesis-show-statistics -x --ff

   # testing
   coverage erase
   pytest --cov --hypothesis-show-statistics
   coverage html

   # linting
   pylint *
   flake8
   mypy -p snmp_fetch -p tests
   bandit -r snmp_fetch

   # clean up imports
   isort -rc --atomic .


Known Limitations
"""""""""""""""""

- The library only supports SNMPv2 at this time.

- `GETBULK_REQUEST` and `NEXT_REQUEST` will always perform a walk.

- Walks will always end if the root of the oid runs past the requested oid.

- Duplicate objects on the same host/request will be silently discarded.

  - This includes the initial request; walks must be performed on an oid prior to the first desired.

  - ENDOFMIBVIEW variable bindings are silently discarded for this same reason.
