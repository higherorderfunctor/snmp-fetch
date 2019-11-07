"""Standard bitstream parsers."""

from typing import Any, Text, Tuple

import numpy as np

from snmp_fetch.df.types.inet_address import ip
from snmp_fetch.df.utils import bytes_to_int


def integer(df: Any, source: Text, **kwargs: Any) -> Tuple[int, np.ndarray]:
    # pylint: disable=unused-argument
    """Extract first element of a numpy array as an integer."""
    return df[source][0], df[source][1:]


def object_identifier(df: Any, source: Text, **kwargs: Any) -> Tuple[np.ndarray, np.ndarray]:
    # pylint: disable=unused-argument
    """Extract an object identifier array as a numpy array."""
    return df[source][1:int(df[source][0])+1], df[source][int(df[source][0])+1:]


def inet_address(df: Any, source: Text, **kwargs: Any) -> Tuple[Any, np.ndarray]:
    """Extract an inet address with leading address size and possible zone."""
    default_zone = kwargs.pop('default_zone', None)
    if df[source][0] == 4:
        return (
            (ip.IPv4Address(bytes_to_int(df[source][1:5])), default_zone),
            df[source][5:]
        )
    if df[source][0] == 16:
        return (
            (ip.IPv6Address(bytes_to_int(df[source][1:17])), default_zone),
            df[source][17:]
        )
    if df[source][0] == 8:
        return (
            (ip.IPv4Address(bytes_to_int(df[source][1:9])), bytes_to_int(df[source][9:13])),
            df[source][13:]
        )
    if df[source][0] == 20:
        return (
            (ip.IPv6Address(bytes_to_int(df[source][1:17])), bytes_to_int(df[source][17:21])),
            df[source][21:]
        )
    raise TypeError('Datatype not understood')
