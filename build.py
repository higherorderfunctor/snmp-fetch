"""Build script for the C extension."""

import os
import re
from typing import Any, MutableMapping

from setuptools import Extension

NETSNMP_BASEDIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'libs'
)
NETSNMP_LIBS = os.popen('net-snmp-config --libs').read()

EXTENSIONS = [
    Extension(
        'snmp_fetch.capi', [
            'src/capi/capimodule.cpp'
        ],
        depends=[
            'src/capi/session.hpp',
            'src/capi/asyncio.hpp',
            'src/capi/results.hpp',
            'src/capi/types.hpp',
            'src/capi/utils.hpp',
            'src/capi/debug.hpp',
        ],
        library_dirs=re.findall(r'-L(\S+)', NETSNMP_LIBS),
        libraries=re.findall(r'-l(\S+)', NETSNMP_LIBS),
        language='c++',
        extra_compile_args=['-std=c++17']
    ),
]


def build(setup_kwargs: MutableMapping[Any, Any]) -> None:
    """Entry point for build script."""
    setup_kwargs.update({'ext_modules': EXTENSIONS})
