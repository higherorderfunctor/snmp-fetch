"""DataFrame helper functions."""

from typing import Any, Callable, Sequence, Text, Union


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
