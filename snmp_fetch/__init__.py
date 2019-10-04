"""Python wrapper to the C API."""

from snmp_fetch.capi import ErrorType, PduType, SnmpConfig, SnmpError, fetch

__all__ = [
    'ErrorType', 'PduType', 'SnmpConfig', 'SnmpError', 'fetch'
]
