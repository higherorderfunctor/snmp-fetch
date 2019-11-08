"""Python wrapper to the C API."""

from typing import Any, Iterator, Optional, Sequence, Text, Tuple, Type

import pandas as pd
from toolz.sandbox.core import unzip

from snmp_fetch.capi import PduType, SnmpConfig, SnmpError, SnmpErrorType
from .decorators import object_type, pipeline_hook
from .distributed import distribute
from .distributed import fetch as distributed_fetch
from .object_type import ObjectType

__all__ = [
    'PduType', 'SnmpConfig', 'SnmpError', 'SnmpErrorType', 'object_type', 'pipeline_hook'
]


def fetch(
        pdu_type: PduType,
        df: Any,
        obj_type: Type[ObjectType],
        config: Optional[SnmpConfig] = None,
        **kwargs: Text
) -> Tuple[Any, Sequence[SnmpError]]:
    """Fetch SNMP results and map to a DataFrame."""
    def _fetch() -> Iterator[Tuple[Any, Sequence[SnmpError]]]:
        for hosts, data, index in distribute(df, None, **kwargs):
            results, errors = distributed_fetch(
                pdu_type,
                hosts,
                obj_type,
                config=config
            )
            yield obj_type.to_pandas(results, data, index), errors

    result_dfs, errors_lists = unzip(list(_fetch()))

    return (
        pd.concat(result_dfs),
        [error for errors in errors_lists for error in errors]
    )
