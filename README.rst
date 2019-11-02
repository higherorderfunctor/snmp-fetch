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

An opinionated python3.7 SNMPv2 package designed for rapid database ingestion.  This package is a source distribution that includes a C module wrapping net-snmp.  No MIB processing is done as part of this package.  The C module copies raw results from net-snmp into numpy arrays for fast post-processing with either numpy or pandas.  Other libraries that wrap net-snmp will typically return control to python between every PDU request-response.  Snmp-fetch is designed to be thread-safe and efficient by walking multiple targets within the C module with the GIL released.  Helper modules are provided to aid in the post-processing with MIB-like definitions for converting the raw data into usable DataFrames.

Prerequisites
"""""""""""""

Snmp-fetch requires python 3.7, a c++17 compiler (currently only supports gcc-8), and cmake 3.12.4+.  No other user installed dependencies should be required for building this package.  Installation may take some time as the build script will download and build pybind11, boost, and a light-weight configured version of net-snmp within the package.

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
   poetry install -E notebooks
   jupyter lab

Development
"""""""""""

`Poetry <https://poetry.eustace.io/>`_ is required for the development of snmp-fetch.

.. code:: console

   # clone the respository
   git clone --recurse-submodules -j8 https://github.com/higherorderfunctor/snmp-fetch.git
   cd snmp-fetch

   # if working off an existing clone, update the current branch
   git pull  # pull the latest code
   git submodule update --init  # pull the latest submodule version

   # setup the virtual environment - mypy uses symbolic links in the 'stubs' directory to
   # expose packages that play nicely with the static type checker
   virtualenv -p python3.7 ENV
   source ENV/bin/activate
   poetry install

.. code:: console

   # C++ headers are in the following folders for linters
   export CPLUS_INCLUDE_PATH="build/temp.linux-x86_64-3.7/include:lib/pybind11/include:lib/Catch2/single_include/catch2"

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

   # C++ testing
   cd build/temp.linux-x86_64-3.7/
   cmake ../.. && make test_capi test


Known Limitations
"""""""""""""""""
- Changes between v0.1.x versions may introduce breaking changes.

- The library only supports SNMPv2 at this time.

- `BULKGET_REQUEST` and `NEXT_REQUEST` will always perform a walk.

- Walks will always end if the root of the OID runs past the requested OID.

- Duplicate objects on the same host/request will be silently discarded.

  - This includes the initial request; walks must be performed on an OID prior to the first desired.

- NO_SUCH_INSTANCE, NO_SUCH_OBJECT, and END_OF_MIB_VIEW response variable bindings are exposed as errors for handling by the client.
