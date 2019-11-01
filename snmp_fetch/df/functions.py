"""Composable DataFrame functions."""

from typing import Any, Callable, List, Optional, Text, Union, cast

import numpy as np
import pandas as pd

from .types.inet_address import IPV4_PREFIX_LOOKUP_TABLE, IPV6_PREFIX_LOOKUP_TABLE, IpNetwork, ip
from .utils import bytes_to_int


def set_index(columns: Union[Text, List[Text]]) -> Callable[[Any], Any]:
    """Return a composable function to set an index on a DataFrame."""
    def _set_index(df: Any) -> Any:
        for column in columns if isinstance(columns, List) else [columns]:
            if column not in df.columns:
                df[column] = None
        return df.set_index(columns)
    return _set_index


def astype(column: Text, dtype: Any) -> Callable[[Any], Any]:
    """Return a composable function to set a dtype of a DataFrame column."""
    def _astype(df: Any) -> Any:
        df[column] = df[column].astype(dtype)
        return df
    return _astype


def decode(column: Text) -> Callable[[Any], Any]:
    """Return a composable function to decode a DataFrame text column."""
    def _decode(df: Any) -> Any:
        df[column] = df[column].str.decode('utf-8', errors='ignore')
        return df
    return _decode


def to_timedelta(
        column: Text, denominator: int = 1, unit: Text = 'seconds'
) -> Callable[[Any], Any]:
    """Return a composable function to convert to a time delta."""
    def _to_timedelta(df: Any) -> Any:
        df[column] = pd.to_timedelta(df[column] // denominator, unit=unit)
        return df
    return _to_timedelta


def drop(**kwargs: Any) -> Any:
    """Return a composable function to drop data from a DataFrame."""
    def _drop(df: Any) -> Any:
        return df.drop(**kwargs)
    return _drop


def to_oid_string(column: Text, size_col: Optional[Text] = '#result_size') -> Callable[[Any], Any]:
    """Return a composable function to convert an uint64 array to an OID string."""
    def _to_oid_string(df: Any) -> Any:
        def arr(x: np.ndarray) -> np.ndarray:
            if size_col is not None:
                return cast(np.ndarray, x[column][:x[size_col] >> 3])
            return cast(np.ndarray, x[column])
        if not df.empty:
            df[column] = (
                df.apply(
                    lambda x: '.' + '.'.join(map(str, arr(x))),
                    axis=1
                )
            )
        return df
    return _to_oid_string


def to_ipv4_address(column: Text) -> Callable[[Any], Any]:
    """Return a composable function to convert a numpy array to an IPv4Address."""
    def _to_ipv4_address(df: Any) -> Any:
        df[column] = df[column].apply(lambda x: ip.IPv4Address(bytes_to_int(x)))
        return df
    return _to_ipv4_address


def to_ipv6_address(column: Text) -> Callable[[Any], Any]:
    """Return a composable function to convert a numpy array to an IPv6Address."""
    def _to_ipv6_address(df: Any) -> Any:
        df[column] = df[column].apply(lambda x: ip.IPv6Address(bytes_to_int(x)))
        return df
    return _to_ipv6_address


def to_cidr_address(
        column: Text, ip_address: Text, mask_or_prefix: Text, **kwargs: Any
) -> Callable[[Any], Any]:
    """Return a composable function to convert an IP address and mask/prefix to a network."""
    def _ip_network(row: Any) -> IpNetwork:
        if not isinstance(row[ip_address], (ip.IPv4Address, ip.IPv6Address)):
            addr = ip.ip_address(row[ip_address])
        else:
            addr = row[ip_address]
        if isinstance(row[mask_or_prefix], int):
            prefix = row[mask_or_prefix]
        elif isinstance(addr, ip.IPv4Address) and isinstance(row[mask_or_prefix], ip.IPv4Address):
            prefix = IPV4_PREFIX_LOOKUP_TABLE[int(row[mask_or_prefix])]
        elif isinstance(addr, ip.IPv6Address) and isinstance(row[mask_or_prefix], ip.IPv6Address):
            prefix = IPV6_PREFIX_LOOKUP_TABLE[int(row[mask_or_prefix])]
        else:
            raise ValueError(
                f'Unable to infer CIDR address from {(row[[ip_address, mask_or_prefix]])}\n'
            )
        return cast(IpNetwork, ip.ip_network((addr, prefix), **kwargs))

    def _to_cidr_address(df: Any) -> Any:
        if df.empty:
            df[column] = None
        else:
            df[column] = df[[ip_address, mask_or_prefix]].apply(_ip_network, axis=1)
        return df
    return _to_cidr_address
