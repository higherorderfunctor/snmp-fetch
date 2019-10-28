"""Python wrapper to the C API."""

from typing import Any, Optional, Sequence, Text, Tuple

import pandas as pd
from toolz.sandbox.core import unzip

from snmp_fetch.capi import PduType, SnmpConfig, SnmpError, SnmpErrorType
from .distributed import distribute
from .distributed import fetch as dfetch
from .distributed import process_response
from .var_bind import var_bind

__all__ = [
    'PduType', 'SnmpConfig', 'SnmpError', 'SnmpErrorType'
]


def fetch(
        pdu_type: PduType,
        df: Any,
        var_binds: Sequence[var_bind],
        config: Optional[SnmpConfig] = None,
        **kwargs: Text
) -> Tuple[Any, Sequence[SnmpError]]:
    """Fetch SNMP results and map to a DataFrame."""
    params = distribute(
        pdu_type,
        df,
        var_binds,
        config,
        batch_size=None,
        **kwargs
    )

    result_dfs, error_lists = unzip([
        process_response(*process_response_params, dfetch(*fetch_params))
        for fetch_params, process_response_params in params
    ])

    return (
        pd.concat(result_dfs),
        [error for errors in error_lists for error in errors]
    )
