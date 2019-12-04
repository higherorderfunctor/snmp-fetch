"""Distributed friendly implementation."""

from typing import Any, Iterator, Optional, Sequence, Text, Tuple, Type

import numpy as np

from . import Community, Config, Host, PduType, SnmpError, Version
from .api import dispatch as api_fetch
from .object_type import ObjectType

RESERVED_COL_NAMES = [
    '#id', '#oid_size', '#result_size', '#result_type', '#oid', '#timestamp'
]

HOST_T = Tuple[int, Text, Text]  # pylint: disable=invalid-name


def fetch(
        pdu_type: PduType,
        hosts: Sequence[HOST_T],
        var_bind: Type[ObjectType],
        parameter: Optional[Text] = None,
        config: Optional[Config] = None
) -> Tuple[Sequence[np.ndarray], Sequence[SnmpError]]:
    """Wrap the C API versions of fetch."""
    return api_fetch(
        pdu_type,
        [Host(i, h, [Community(Version.V2C, c)]) for i, h, c in hosts],
        var_bind.null_var_binds(parameter),
        config=config if config is not None else Config()
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
        **kwargs: Any
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
    df.index = df.index.set_names(['#id'])
    df = df.reset_index()

    def default_get_hosts(df: Any) -> Sequence[HOST_T]:
        return [
            (i, str(h), c) for i, h, c
            in df[['#id', host_column, community_column]].values
        ]

    get_hosts = kwargs.pop('get_hosts', default_get_hosts)

    def _prepare(df: Any) -> Tuple[Sequence[HOST_T], Any, Optional[Sequence[Text]]]:
        return (
            get_hosts(df),
            df.set_index('#id'),
            index
        )

    if batch_size:
        batched = [df[i:i+batch_size] for i in range(0, df.shape[0], batch_size)]
        for batch in batched:
            yield _prepare(batch)
        return
    yield _prepare(df)
