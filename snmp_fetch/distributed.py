"""Distributed friendly implementation."""

from typing import Any, Iterator, Optional, Sequence, Text, Tuple, Type

import numpy as np

from . import PduType, SnmpConfig, SnmpError
from .api import fetch as api_fetch
from .object_type import ObjectType

RESERVED_COL_NAMES = [
    '#oid_size', '#result_size', '#result_type', '#oid', '#timestamp'
]

HOST_T = Tuple[int, Text, Text]  # pylint: disable=invalid-name


def fetch(
        pdu_type: PduType,
        hosts: Sequence[HOST_T],
        var_bind: Type[ObjectType],
        config: Optional[SnmpConfig] = None
) -> Tuple[Sequence[np.ndarray], Sequence[SnmpError]]:
    """Wrap the C API versions of fetch."""
    return api_fetch(
        pdu_type,
        hosts,
        var_bind.null_var_binds(),
        config=config if config is not None else SnmpConfig()
    )


def to_pandas(
        object_type: Type[ObjectType], response: Tuple[Sequence[np.ndarray], Sequence[SnmpError]],
        data: Optional[Any] = None, index: Optional[Sequence[Text]] = None
) -> Tuple[Any, Sequence[SnmpError]]:
    """Wrap ObjectType.to_pandas to deconstruct the response tuple."""
    results, errors = response
    return object_type.to_pandas(results, data, index), errors


def distribute(
        df: Any,
        batch_size: Optional[int] = None,
        **kwargs: Text
) -> Iterator[Tuple[Sequence[HOST_T], Any, Optional[Sequence[Text]]]]:
    """Fetch SNMP results and map to a DataFrame."""
    err_col_names = set([*df.index.names, *df.columns]).intersection(RESERVED_COL_NAMES)
    if err_col_names:
        raise ValueError(
            f'DataFrame contains the following reserved column names: {err_col_names}'
        )

    host_column = kwargs.pop('host', 'host')
    community_column = kwargs.pop('snmp_community', 'snmp_community')

    index = None
    if df.index.names is not None and [i for i in df.index.names if i is not None]:
        index = df.index.names
    df = df.reset_index()
    df.index = df.index.set_names(['#index'])
    df = df.reset_index()

    def _prepare(df: Any) -> Tuple[Sequence[HOST_T], Any, Optional[Sequence[Text]]]:
        return (
            [
                (i, str(h), c) for i, h, c
                in df[['#index', host_column, community_column]].values
            ],
            df.set_index('#index'),
            index
        )

    if batch_size:
        batched = [df[i:i+batch_size] for i in range(0, df.shape[0], batch_size)]
        for batch in batched:
            yield _prepare(batch)
        return
    yield _prepare(df)
