"""Pytest fixtures."""

import subprocess
import time
from typing import Iterator

import pytest


@pytest.fixture(scope='session', autouse=True)
def snmpsimd() -> Iterator[None]:  # type: ignore
    """Start the simulation agent for testing."""
    process = subprocess.Popen(
        [
            'snmpsimd.py',
            '--agent-udpv4-endpoint=127.0.0.1:1161',
            '--agent-udpv6-endpoint=[::1]:1161'
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False
    )
    time.sleep(5)
    yield
    process.kill()
