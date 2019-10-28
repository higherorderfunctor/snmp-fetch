"""Distributed friendly implementation."""

from functools import reduce
from typing import Any, Optional, Sequence, Text, Tuple, cast

import numpy as np
import pandas as pd

from . import PduType, SnmpConfig, SnmpError
from .capi import fetch as capi_fetch
from .var_bind import var_bind

RESERVED_COL_NAMES = [
    '#oid_size', '#result_size', '#result_type', '#oid', '#ipadding', '#dpadding', '#timestamp',
    '#timestamp'
]

HOST_T = Tuple[int, Text, Text]  # pylint: disable=invalid-name


def merge(a: Any, b: Any) -> Any:
    """Merge two DataFrame results."""
    df = pd.merge(a, b, how='outer', left_index=True, right_index=True)
    df['#timestamp'] = df[['#timestamp_x', '#timestamp_y']].max(axis=1)
    return df.drop(columns=['#timestamp_x', '#timestamp_y'])


def prepare_column(arr: np.ndarray, vb: var_bind) -> Any:
    """Convert structured numpy array into DataFrame."""
    view = arr.view(vb.cstruct())
    df = pd.DataFrame.from_records(
        view.tolist(), columns=view.dtype.names
    )
    df = vb.op(df)
    if not df.index.empty:
        df = df.reset_index().set_index(['#index', *df.index.names])
    else:
        df = df.set_index('#index')
    df = df.drop(columns={
        '#oid_size', '#result_size', '#result_type', '#oid', '#ipadding', '#dpadding'
    }.intersection(df.columns))
    return df


def fetch(
        pdu_type: PduType,
        hosts: Sequence[HOST_T],
        var_binds: Sequence[var_bind],
        config: SnmpConfig,
) -> Tuple[Sequence[np.ndarray], Sequence[SnmpError]]:
    """Wrap the C API versions of fetch."""
    return capi_fetch(
        pdu_type,
        hosts,
        [vb() for vb in var_binds],
        config=config if config is not None else SnmpConfig()
    )


def process_response(
        df: Any, var_binds: Sequence[var_bind], idx: Sequence[Text],
        response: Tuple[Sequence[np.ndarray], Sequence[SnmpError]]
) -> Tuple[Any, Sequence[SnmpError]]:
    """Process SNMP response into a results DataFrame and errors list."""
    results, errors = response
    results_df = reduce(
        merge, [prepare_column(r, vb) for r, vb in zip(results, var_binds)]
    )
    results_df = results_df.reset_index().set_index('#index').merge(
        df.set_index('#index'), how='outer', left_index=True, right_index=True
    )
    return results_df.reset_index(drop=True).set_index(idx), errors


def distribute(
        pdu_type: PduType,
        df: Any,
        var_binds: Sequence[var_bind],
        config: Optional[SnmpConfig] = None,
        batch_size: Optional[int] = None,
        **kwargs: Text
) -> Sequence[Tuple[
    Tuple[PduType, Sequence[HOST_T], Sequence[var_bind], SnmpConfig],
    Tuple[Any, Sequence[var_bind], Sequence[Text]]
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
            Tuple[PduType, Sequence[HOST_T], Sequence[var_bind], SnmpConfig],
            Tuple[Any, Sequence[var_bind], Sequence[Text]]
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
