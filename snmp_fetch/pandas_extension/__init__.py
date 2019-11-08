"""Extended DataFrame functionality."""

from typing import Any, Text, Tuple, Union, cast

import numpy as np
import pandas as pd

from snmp_fetch.utils import cuint8_to_int
from .types import ip_address as ip


@pd.api.extensions.register_dataframe_accessor('inet')
class InetDataFrameAccessor:
    # pylint: disable=too-few-public-methods
    """Inet DataFrame accessor."""

    obj: Any

    def __init__(self, obj: Any) -> None:
        """Initialize the pandas extension."""
        self.obj = obj

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

        def __getitem__(self, ss: Union[int, slice, Tuple[Union[int, slice]]]) -> Any:
            """Slice the buffer."""
            if isinstance(ss, (int, slice)):
                return self.obj.apply(lambda x: x[ss])
            if isinstance(ss, tuple):
                return pd.DataFrame(self.obj.apply(lambda x: [x[s] for s in ss]).tolist())
            raise RuntimeError(f'Not a valid input slice: {ss}')

        def to_inet_address(self, default_zone: Any = None) -> Any:
            """Extract an inet address with leading address size and possible zone."""
            def _to_inet_address(buffer: np.ndarray) -> Tuple[ip.IP_ADDRESS_T, Any, np.ndarray]:
                if buffer[0] == 4:
                    return (
                        ip.IPv4Address(cuint8_to_int(buffer[1:5])),
                        default_zone,
                        buffer[5:]
                    )
                if buffer[0] == 16:
                    return (
                        ip.IPv6Address(cuint8_to_int(buffer[1:17])),
                        default_zone,
                        buffer[17:]
                    )
                if buffer[0] == 8:
                    return (
                        ip.IPv4Address(cuint8_to_int(buffer[1:9])),
                        cuint8_to_int(buffer[9:13]),
                        buffer[13:]
                    )
                if buffer[0] == 20:
                    return (
                        ip.IPv6Address(cuint8_to_int(buffer[1:17])),
                        cuint8_to_int(buffer[17:21]),
                        buffer[21:]
                    )
                raise TypeError('Datatype not understood')
            return pd.DataFrame(
                self.obj.apply(_to_inet_address).tolist(),
                columns=['inet_address', 'zone', '_buffer']
            )

        def to_object_identifier(self) -> Any:
            """Extract an object identifier buffer as a string."""
            def _to_object_identifier(buffer: np.ndarray) -> Tuple[Text, np.ndarray]:
                return (
                    '.'+'.'.join(buffer[1:int(buffer[0])+1].astype(str)),
                    buffer[int(buffer[0])+1:]
                )
            return pd.DataFrame(
                self.obj.apply(_to_object_identifier).tolist(),
                columns=['object_identifier', '_buffer']
            )

    def __init__(self, obj: Any) -> None:
        """Initialize the pandas extension."""
        self.obj = obj
        self.buffer = self.InetSeriesBufferAccessor(obj)

    def _to_inet_address(self, default_zone: Any = None) -> Any:
        """Extract an inet address with leading address size and possible zone."""
        return self.buffer.to_inet_address(default_zone)[['inet_address', 'zone']]

    def to_object_identifier(self) -> Any:
        """Extract an object identifier buffer as a string."""
        return self.buffer.to_object_identifier()[['object_identifier']]

    def to_timedelta(
            self, denominator: int = 1, unit: Text = 'seconds'
    ) -> Any:
        """Return a composable function to convert to a time delta."""
        return pd.to_timedelta(self.obj // denominator, unit=unit)
