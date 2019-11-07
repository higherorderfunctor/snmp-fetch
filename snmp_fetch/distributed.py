"""Distributed friendly implementation."""

from functools import reduce
from typing import Any, Optional, Sequence, Text, Tuple, Type, cast

import numpy as np
import pandas as pd

from . import PduType, SnmpConfig, SnmpError
from .capi import fetch as capi_fetch
from .var_bind import VarBind

RESERVED_COL_NAMES = [
    '#oid_size', '#result_size', '#result_type', '#oid', '#timestamp'
]

HOST_T = Tuple[int, Text, Text]  # pylint: disable=invalid-name


def fetch(
        pdu_type: PduType,
        hosts: Sequence[HOST_T],
        var_bind: Type[VarBind],
        config: SnmpConfig
) -> Tuple[Sequence[np.ndarray], Sequence[SnmpError]]:
    """Wrap the C API versions of fetch."""
    return capi_fetch(
        pdu_type,
        hosts,
        var_bind.null_var_binds(),
        config=config if config is not None else SnmpConfig()
    )


def distribute(
        pdu_type: PduType,
        df: Any,
        var_binds: Sequence[VarBind],
        config: Optional[SnmpConfig] = None,
        batch_size: Optional[int] = None,
        **kwargs: Text
) -> Sequence[Tuple[
    Tuple[PduType, Sequence[HOST_T], Sequence[VarBind], SnmpConfig],
    Tuple[Any, Sequence[VarBind], Sequence[Text]]
]]:
    """Fetch SNMP results and map to a DataFrame."""
    err_col_names = set([*df.index.names, *df.columns]).intersection(RESERVED_COL_NAMES)
    if err_col_names:
        raise ValueError(
            f'DataFrame contains the following reserved column names: {err_col_names}'
        )

    if config is None:
        config = SnmpConfig()

    host_column = kwargs.pop('host', 'host')
    community_column = kwargs.pop('snmp_community', 'snmp_community')

    idx = df.index.names
    df = df.reset_index()
    df.index = df.index.set_names(['#index'])
    df = df.reset_index()

    def _prepare(df: Any) -> Tuple[
            Tuple[PduType, Sequence[HOST_T], Sequence[VarBind], SnmpConfig],
            Tuple[Any, Sequence[VarBind], Sequence[Text]]
    ]:
        # mypy does not detect that closure of config is no longer optional
        return ((  # type: ignore
            pdu_type,
            [
                (i, str(h), c) for i, h, c
                in df[['#index', host_column, community_column]].values
            ],
            var_binds,
            config
        ), (
            df,
            var_binds,
            cast(Sequence[Text], idx)
        ))

    if batch_size:
        batched = [df[i:i+batch_size] for i in range(0, df.shape[0], batch_size)]
        return [_prepare(batch) for batch in batched]
    return [_prepare(df)]
