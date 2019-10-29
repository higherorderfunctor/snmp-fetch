"""DataFrame helper functions."""

from typing import Any, Callable, Sequence, Text, Union

import pandas as pd


def set_index(columns: Union[Text, Sequence[Text]]) -> Callable[[Any], Any]:
    """Return a function to set an index on a DataFrame."""
    def _set_index(df: Any) -> Any:
        return df.set_index(columns)
    return _set_index


def astype(column: Text, dtype: Any) -> Callable[[Any], Any]:
    """Return a function to set a dtype of a DataFrame column."""
    def _astype(df: Any) -> Any:
        df[column] = df[column].astype(dtype)
        return df
    return _astype


def decode(column: Text) -> Callable[[Any], Any]:
    """Return a function to decode a DataFrame text column."""
    def _decode(df: Any) -> Any:
        df[column] = df[column].str.decode('utf-8', errors='ignore')
        return df
    return _decode


def to_timedelta(
        column: Text, denominator: int = 1, unit: Text = 'seconds'
) -> Callable[[Any], Any]:
    """Return a function to convert to a time delta."""
    def _to_timedelta(df: Any) -> Any:
        df[column] = pd.to_timedelta(df[column] // denominator, unit=unit)
        return df
    return _to_timedelta


def to_oid_string(column: Text) -> Callable[[Any], Any]:
    """Return a funct to convert to an OID string."""
    def _to_oid_string(df: Any) -> Any:
        if not df.empty:
            df[column] = (
                df[['#result_size', column]]
                .apply(
                    lambda x: '.' + '.'.join(map(str, x[column][:x['#result_size'] >> 3])),
                    axis=1
                )
            )
        return df
    return _to_oid_string
