# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['snmp_fetch', 'snmp_fetch.df', 'snmp_fetch.df.types', 'snmp_fetch.fp']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0',
 'numpy>=1.16,<2.0',
 'pandas>=0.25,<0.26',
 'toolz>=0.10.0,<0.11.0']

extras_require = \
{'notebooks': ['jupyterlab>=1.1,<2.0', 'distributed>=2.6,<3.0']}

setup_kwargs = {
    'name': 'snmp-fetch',
    'version': '0.1.7.1',
    'description': 'An opinionated python SNMPv2 library built for rapid database ingestion.',
    'long_description': 'snmp-fetch\n==========\n\n|Version badge| |Python version badge| |PyPI format badge| |Build badge| |Coverage badge|\n\n.. |Version badge| image:: https://img.shields.io/pypi/v/snmp-fetch\n   :target: https://pypi.org/project/snmp-fetch/\n\n.. |Python version badge| image:: https://img.shields.io/pypi/pyversions/snmp-fetch\n   :alt: PyPI - Python Version\n   :target: https://pypi.org/project/snmp-fetch/\n  \n.. |PyPI format badge| image:: https://img.shields.io/pypi/format/snmp-fetch\n   :alt: PyPI - Format\n   :target: https://pypi.org/project/snmp-fetch/\n\n.. |Build badge| image:: https://travis-ci.org/higherorderfunctor/snmp-fetch.svg?branch=master\n   :target: https://travis-ci.org/higherorderfunctor/snmp-fetch\n\n.. |Coverage badge| image:: https://coveralls.io/repos/github/higherorderfunctor/snmp-fetch/badge.svg\n   :target: https://coveralls.io/github/higherorderfunctor/snmp-fetch\n\nAn opinionated python3.7 SNMPv2 package designed for rapid database ingestion.  This package is a source distribution that includes a C module wrapping net-snmp.  No MIB processing is done as part of this package.  The C module copies raw results from net-snmp into numpy arrays for fast post-processing with either numpy or pandas.  Other libraries that wrap net-snmp will typically return control to python between every PDU request-response.  Snmp-fetch is designed to be thread-safe and efficient by walking multiple targets within the C module with the GIL released.  Helper modules are provided to aid in the post-processing with MIB-like definitions for converting the raw data into usable DataFrames.\n\nPrerequisites\n"""""""""""""\n\nSnmp-fetch requires python 3.7, a c++17 compiler (currently only supports gcc-8), and cmake 3.12.4+.  No other user installed dependencies should be required for building this package.\n\n.. ATTENTION::\n\n   Installation can take awhile as the install script will download boost and download and build a light-weight version of net-snmp 5.8 within the package.\n\n   The boost download can take awhile as it clones each submodule as oppose to downloading the compressed distribution.  There is an issue with downloading the compressed distribution via cmake with 302 redirects to a file failing in cURL.\n\n   The cmake script will attempt to detect the number of cores on the host machine to speedup download and build times.  Expect installation times to range from 5 minutes (4 cores with hyperthreading) to 30+ minutes (1 core).\n\nInstallation\n""""""""""""\n\n.. code:: console\n\n   # poetry\n   poetry add snmp-fetch --no-dev\n   # pip\n   pip install snmp-fetch\n\nExamples\n""""""""\n\nThe examples use jupyter and the dependencies can be installed using the following:\n\n.. code:: console\n\n   git clone --recurse-submodules -j8 https://github.com/higherorderfunctor/snmp-fetch.git\n   cd snmp_fetch\n   virtualenv -p python3.7 ENV\n   source ENV/bin/activate\n   poetry install -E notebooks\n   jupyter lab\n\nDevelopment\n"""""""""""\n\n`Poetry <https://poetry.eustace.io/>`_ is required for the development of snmp-fetch.\n\n.. code:: console\n\n   # clone the respository\n   git clone --recurse-submodules -j8 https://github.com/higherorderfunctor/snmp-fetch.git\n   cd snmp-fetch\n\n   # if working off an existing clone, update the current branch\n   git pull  # pull the latest code\n   git submodule update --init --recursive  # pull the latest submodule version\n\n   # setup the virtual environment - mypy uses symbolic links in the \'stubs\' directory to\n   # expose packages that play nicely with the static type checker\n   virtualenv -p python3.7 ENV\n   source ENV/bin/activate\n   poetry install\n\n.. code:: console\n\n   # C++ headers are in the following folders for linters\n   export CPLUS_INCLUDE_PATH="build/temp.linux-x86_64-3.7/include:lib/pybind11/include:lib/Catch2/single_include/catch2:lib/boost"\n\n   # python linting\n   poetry run isort -rc --atomic .\n   poetry run pylint snmp_fetch tests\n   poetry run flake8 snmp_fetch tests\n   poetry run mypy -p snmp_fetch -p tests\n   poetry run bandit -r snmp_fetch\n\n   # C++ linting\n   # TODO\n\n   # python testing\n   poetry run pytest -v --hypothesis-show-statistics tests\n   # fail fast testing\n   poetry run pytest -x --ff tests\n\n   # C++ testing\n   pushd build/temp.linux-x86_64-3.7/\n   cmake -DBUILD_TESTING=ON ../.. && make test_capi test\n   popd\n\nUpgrading Dependencies\n----------------------\n\n.. code:: console\n\n   # boost\n   rm -rf lib/boost\n   mkdir lib/boost\n   wget https://dl.bintray.com/boostorg/release/X.Y.Z/source/boost_X_Y_Z.tar.gz\n   tar -xvf boost_X_Y_Z.tar.gz\n   cd boost_X_Y_Zi\n   ./bootstrap.sh\n   cd tools/bcp\n   ../../b2\n   cd ../../\n   chmod +x bin.v2/tools/bcp \n   bin.v2/tools/bcp/gcc-8/release/link-static/bcp LICENSE_1_0.txt boost/format.hpp boost/range/combine.hpp ../lib/boost\n   cd ..\n   rm -rf boost_X_Y_Z*\n\n\n\nKnown Limitations\n"""""""""""""""""\n- Changes between v0.1.x versions may introduce breaking changes.\n\n- The library only supports SNMPv2 at this time.\n\n- `BULKGET_REQUEST` and `NEXT_REQUEST` will always perform a walk.\n\n- Walks will always end if the root of the OID runs past the requested OID.\n\n- Duplicate objects on the same host/request will be silently discarded.\n\n  - This includes the initial request; walks must be performed on an OID prior to the first desired.\n\n- NO_SUCH_INSTANCE, NO_SUCH_OBJECT, and END_OF_MIB_VIEW response variable bindings are exposed as errors for handling by the client.\n',
    'author': 'Christopher Aubut',
    'author_email': 'christopher@aubut.me',
    'url': 'https://github.com/higherorderfunctor/snmp-fetch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
