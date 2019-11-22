"""Extended DataFrame functionality."""

from typing import Any, Iterator, Optional, Sequence, Text, Tuple, Union, cast

import numpy as np
import pandas as pd

from snmp_fetch.utils import cuint8_to_int
from .types import ip_address as ip


def column_names(
        n: Optional[int] = None, alphabet: Sequence[Text] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
) -> Iterator[Text]:
    """Generate unique temporary column names."""
    base_gen = column_names(alphabet=alphabet)
    base = ''
    letters = alphabet
    while True:
        if n is not None:
            if n <= 0:
                return
            n = n - 1
        if not letters:
            base = next(base_gen)  # pylint: disable=stop-iteration-return  # infinite generator
            letters = alphabet
        column, letters = letters[0], letters[1:]
        yield base + column


@pd.api.extensions.register_dataframe_accessor('inet')
class InetDataFrameAccessor:
    # pylint: disable=too-few-public-methods
    """Inet DataFrame accessor."""

    obj: Any

    def __init__(self, obj: Any) -> None:
        """Initialize the pandas extension."""
        self.obj = obj

    def to_interface_address(self) -> Any:
        """Return a composable function to convert an IP address and mask/prefix to a network."""
        def _to_int_address(
                objs: Tuple[ip.IP_ADDRESS_T, Union[int, ip.IP_ADDRESS_T]]
        ) -> ip.IP_INTERFACE_T:
            ip_address, cidr_or_mask = objs
            if isinstance(cidr_or_mask, ip.IPv4Address):
                cidr_or_mask = ip.IPV4_PREFIX_LOOKUP_TABLE[int(cidr_or_mask)]
            if isinstance(cidr_or_mask, ip.IPv6Address):
                cidr_or_mask = ip.IPV6_PREFIX_LOOKUP_TABLE[int(cidr_or_mask)]
            return cast(
                ip.IP_INTERFACE_T,
                ip.ip_interface((ip_address, cidr_or_mask))
            )

        if self.obj.empty:
            return pd.Series([])
        return self.obj.apply(_to_int_address, axis=1)

    def to_cidr_address(self, strict: bool = False) -> Any:
        """Return a composable function to convert an IP address and mask/prefix to a network."""
        def _to_cidr_address(
                objs: Tuple[ip.IP_ADDRESS_T, Union[int, ip.IP_ADDRESS_T]]
        ) -> ip.IP_NETWORK_T:
            ip_address, cidr_or_mask = objs
            if isinstance(cidr_or_mask, ip.IPv4Address):
                cidr_or_mask = ip.IPV4_PREFIX_LOOKUP_TABLE[int(cidr_or_mask)]
            if isinstance(cidr_or_mask, ip.IPv6Address):
                cidr_or_mask = ip.IPV6_PREFIX_LOOKUP_TABLE[int(cidr_or_mask)]
            return cast(
                ip.IP_NETWORK_T,
                ip.ip_network((ip_address, cidr_or_mask), strict=strict)
            )

        if self.obj.empty:
            return pd.Series([])
        return self.obj.apply(_to_cidr_address, axis=1)


@pd.api.extensions.register_series_accessor('inet')
class InetSeriesAccessor:
    # pylint: disable=too-few-public-methods
    """Inet Series accessor."""

    obj: Any
    buffer: 'InetSeriesAccessor.InetSeriesBufferAccessor'

    class InetSeriesBufferAccessor:
        """Inet Series buffer accessor."""

        obj: Any

        def __init__(self, obj: Any) -> None:
            """Initialize the pandas extension."""
            self.obj = obj

        def __getitem__(self, ss: Union[int, slice, Tuple[Union[int, slice], ...]]) -> Any:
            """Slice the buffer."""
            if isinstance(ss, (int, slice)):
                return self.obj.apply(lambda x: x[ss])
            if isinstance(ss, tuple):
                return pd.DataFrame(
                    self.obj.apply(lambda x: [x[s] for s in ss]).tolist(),
                    columns=list(column_names(len(ss))),
                    index=self.obj.index
                )
            raise RuntimeError(f'Not a valid input slice: {ss}')

        def chunk(self) -> Any:
            """Slice the buffer by a sized parameter."""
            return pd.DataFrame(
                self.obj.apply(lambda x: (x[1:int(x[0])+1], x[int(x[0])+1:])).tolist(),
                columns=list(column_names(2)),
                index=self.obj.index
            )

    def __init__(self, obj: Any) -> None:
        """Initialize the pandas extension."""
        self.obj = obj
        self.buffer = self.InetSeriesBufferAccessor(obj)

    def to_inet_address(self, default_zone: Any = None) -> Any:
        """Extract an inet address with leading address size and possible zone."""
        def _to_inet_address(buffer: np.ndarray) -> Tuple[ip.IP_ADDRESS_T, Any]:
            if len(buffer) == 4:
                return (
                    ip.IPv4Address(cuint8_to_int(buffer)),
                    default_zone
                )
            if len(buffer) == 16:
                return (
                    ip.IPv6Address(cuint8_to_int(buffer)),
                    default_zone
                )
            if len(buffer) == 8:
                return (
                    ip.IPv4Address(cuint8_to_int(buffer[:8])),
                    cuint8_to_int(buffer[8:])
                )
            if len(buffer) == 20:
                return (
                    ip.IPv6Address(cuint8_to_int(buffer[:16])),
                    cuint8_to_int(buffer[16:])
                )
            raise TypeError('Datatype not understood')
        return pd.DataFrame(
            self.obj.apply(_to_inet_address).tolist(),
            columns=list(column_names(2)),
            index=self.obj.index
        )

    def to_object_identifier(self) -> Any:
        """Extract an object identifier buffer as a string."""
        def _to_object_identifier(buffer: np.ndarray) -> Text:
            return '.'+'.'.join(buffer.astype(str))
        return self.obj.apply(_to_object_identifier)

    def to_timedelta(
            self, denominator: int = 1, unit: Text = 'seconds'
    ) -> Any:
        """Return a composable function to convert to a time delta."""
        return pd.to_timedelta(self.obj // denominator, unit=unit)
