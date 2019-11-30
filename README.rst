netframe
========

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

Netframe is an opinionated python3.7+ package for working with network data in pandas.  It features pandas extensions and an integrated SNMPv2 client.  This package is a source distribution that includes a C++ module wrapping net-snmp.  No MIB processing is done as part of this package.  The C module copies raw results from net-snmp into numpy arrays for fast post-processing in pandas.  Other libraries that wrap net-snmp will typically return control to python between every PDU request-response.  Netframe is designed to be thread-safe and efficient by walking multiple targets within the C module with the GIL released.

Prerequisites
"""""""""""""

Netframe requires python 3.7+, gcc-8, and cmake 3.12.4+.  No other user installed dependencies should be required for building this package.

.. ATTENTION::

   Installation can take awhile as the install script will build a light-weight version of net-snmp 5.8 within the package.

   The cmake script will attempt to detect the number of cores on the host machine to speedup download and build times.  Expect installation times to range from 5 minutes (4 cores with hyperthreading) to 30+ minutes (1 core).

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

   git clone --recurse-submodules -j8 https://github.com/higherorderfunctor/snmp-fetch.git
   cd snmp_fetch
   virtualenv -p python3.7 ENV
   source ENV/bin/activate
   poetry install -E notebooks
   jupyter lab

Development
"""""""""""

`Poetry <https://poetry.eustace.io/>`_ is required for the development of netframe.

.. code:: console

   # clone the respository
   git clone --recurse-submodules -j8 https://github.com/higherorderfunctor/snmp-fetch.git
   cd snmp-fetch

   # if working off an existing clone, update the current branch
   git pull  # pull the latest code
   git submodule update --init --recursive --depth=1  # pull the latest submodule version

   # set the base python version (3.7 or 3.8)
   export BASE_PYTHON_VERSION=3.7

   # Setup the virtual environment.  Symbolic links are located in the 'stubs' directory to
   # this virtual environment location to expose packages that play nicely with mypy.
   virtualenv -p python${BASE_PYTHON_VERSION} ENV
   export MYPYPATH=stubs/linux-x86_64-${BASE_PYTHON_VERSION}
   source ENV/bin/activate
   poetry install

.. code:: console

   # C++ headers are in the following folders for linters
   export CPLUS_INCLUDE_PATH="build/temp.linux-x86_64-${BASE_PYTHON_VERSION}/include:lib/pybind11/include:lib/boost"

   # python linting
   poetry run isort -rc --atomic .
   poetry run pylint snmp_fetch tests
   poetry run flake8 snmp_fetch tests
   poetry run mypy -p snmp_fetch -p tests
   poetry run bandit -r snmp_fetch
   # TODO: C++ Linting

   # testing
   poetry run pytest -x -ff tests

Upgrading Dependencies
----------------------

.. code:: console

   # boost
   rm -rf lib/boost
   mkdir lib/boost
   wget https://dl.bintray.com/boostorg/release/X.Y.Z/source/boost_X_Y_Z.tar.gz
   tar -xvf boost_X_Y_Z.tar.gz
   cd boost_X_Y_Zi
   ./bootstrap.sh
   cd tools/bcp
   ../../b2
   cd ../../
   chmod +x bin.v2/tools/bcp 
   bin.v2/tools/bcp/gcc-8/release/link-static/bcp LICENSE_1_0.txt boost/format.hpp boost/range/combine.hpp ../lib/boost
   cd ..
   rm -rf boost_X_Y_Z*

Known Limitations
"""""""""""""""""
- Changes between v0.1.x versions may introduce breaking changes.

- The library only supports SNMPv2 at this time.

- `BULKGET` and `NEXT` will always perform a walk.

- Walks will always end if the root of the OID runs past the requested OID.

- Duplicate objects on the same host/request will be silently discarded.

  - This includes the initial request; walks must be performed on an OID prior to the first desired.

- NO_SUCH_INSTANCE, NO_SUCH_OBJECT, and END_OF_MIB_VIEW response variable bindings are exposed as errors for handling by the client.
