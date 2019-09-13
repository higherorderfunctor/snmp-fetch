"""Datatype tests."""

import ipaddress as ip
from functools import partial
from operator import itemgetter
from typing import List

import hypothesis
import hypothesis.strategies as st
import numpy as np
from toolz.functoolz import compose

from snmp_fetch.dtype import (
    IPV4_MASK_LOOKUP_TABLE, IPV6_MASK_LOOKUP_TABLE, cast_ip_array, ip_address,
    ip_interface, ip_network
)
from snmp_fetch.fp import star


@hypothesis.given(
    ipv4_address=st.lists(  # type: ignore
        st.integers(0, 255), max_size=4, min_size=4
    )
)
def test_ipv4_inet_address(ipv4_address: List[int]) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv4 address."""
    data = np.array([1, 4, *ipv4_address], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 4))
        ])
    )[0]
    addr, zone = compose(
        partial(ip_address, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert isinstance(addr, ip.IPv4Address)
    assert int(addr) == int.from_bytes(
        np.array(ipv4_address, dtype=np.uint8).tobytes(), byteorder='big'
    )
    assert zone == -1


@hypothesis.given(
    ipv6_address=st.lists(  # type: ignore
        st.integers(0, 255), max_size=16, min_size=16
    )
)
def test_ipv6_inet_address(ipv6_address: List[int]) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv6 address."""
    data = np.array([2, 16, *ipv6_address], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 16))
        ])
    )[0]
    addr, zone = compose(
        partial(ip_address, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert isinstance(addr, ip.IPv6Address)
    assert int(addr) == int.from_bytes(
        np.array(ipv6_address, dtype=np.uint8).tobytes(), byteorder='big'
    )
    assert zone == -1


@hypothesis.given(
    ipv4_address=st.lists(  # type: ignore
        st.integers(0, 255), max_size=4, min_size=4
    ),
    zone=st.lists(
        st.integers(0, 255), max_size=4, min_size=4
    ),
)
def test_ipv4z_inet_address(ipv4_address: List[int], zone: List[int]) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv4z address."""
    data = np.array([3, 8, *ipv4_address, *zone], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 8))
        ])
    )[0]
    addr, _zone = compose(
        partial(ip_address, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert isinstance(addr, ip.IPv4Address)
    assert int(addr) == int.from_bytes(
        np.array(ipv4_address, dtype=np.uint8).tobytes(), byteorder='big'
    )
    assert _zone == int.from_bytes(
        np.array(zone, dtype=np.uint8).tobytes(), byteorder='big'
    )


@hypothesis.given(
    ipv6_address=st.lists(  # type: ignore
        st.integers(0, 255), max_size=16, min_size=16
    ),
    zone=st.lists(
        st.integers(0, 255), max_size=4, min_size=4
    ),
)
def test_ipv6z_inet_address(ipv6_address: List[int], zone: List[int]) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv6z address."""
    data = np.array([4, 20, *ipv6_address, *zone], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 20))
        ])
    )[0]
    addr, _zone = compose(
        partial(ip_address, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert int(addr) == int.from_bytes(
        np.array(ipv6_address, dtype=np.uint8).tobytes(), byteorder='big'
    )
    assert _zone == int.from_bytes(
        np.array(zone, dtype=np.uint8).tobytes(), byteorder='big'
    )


@hypothesis.given(
    ipv4_network=st.lists(  # type: ignore
        st.integers(0, 255), max_size=4, min_size=4
    ),
    prefix_len=st.integers(0, 32)
)
def test_ipv4_ip_prefix_network(
        ipv4_network: List[int], prefix_len: int
) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv4 network."""
    data = np.array([1, 4, *ipv4_network], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 4))
        ])
    )[0]
    addr, zone = compose(
        partial(ip_network, mask=prefix_len, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert isinstance(addr, ip.IPv4Network)
    assert int(addr.network_address) == int.from_bytes(
        np.array(ipv4_network, dtype=np.uint8).tobytes(), byteorder='big'
    ) & IPV4_MASK_LOOKUP_TABLE[prefix_len]
    assert addr.prefixlen == prefix_len
    assert zone == -1


@hypothesis.given(
    ipv4_network=st.lists(  # type: ignore
        st.integers(0, 255), max_size=4, min_size=4
    ),
    prefix_len=st.integers(0, 32)
)
def test_ipv4_ip_mask_network(
        ipv4_network: List[int], prefix_len: int
) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv4 network."""
    data = np.array([1, 4, *ipv4_network], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 4))
        ])
    )[0]
    mask = IPV4_MASK_LOOKUP_TABLE[prefix_len].to_bytes(4, 'big')
    addr, zone = compose(
        partial(ip_network, mask=mask, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert isinstance(addr, ip.IPv4Network)
    assert int(addr.network_address) == int.from_bytes(
        np.array(ipv4_network, dtype=np.uint8).tobytes(), byteorder='big'
    ) & IPV4_MASK_LOOKUP_TABLE[prefix_len]
    assert addr.prefixlen == prefix_len
    assert zone == -1


@hypothesis.given(
    ipv6_network=st.lists(  # type: ignore
        st.integers(0, 255), max_size=16, min_size=16
    ),
    prefix_len=st.integers(0, 128)
)
def test_ipv6_ip_prefix_network(
        ipv6_network: List[int], prefix_len: int
) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv6 network."""
    data = np.array([2, 16, *ipv6_network], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 16))
        ])
    )[0]
    addr, zone = compose(
        partial(ip_network, mask=prefix_len, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert isinstance(addr, ip.IPv6Network)
    assert int(addr.network_address) == int.from_bytes(
        np.array(ipv6_network, dtype=np.uint8).tobytes(), byteorder='big'
    ) & IPV6_MASK_LOOKUP_TABLE[prefix_len]
    assert addr.prefixlen == prefix_len
    assert zone == -1


@hypothesis.given(
    ipv6_network=st.lists(  # type: ignore
        st.integers(0, 255), max_size=16, min_size=16
    ),
    prefix_len=st.integers(0, 128)
)
def test_ipv6_ip_mask_network(
        ipv6_network: List[int], prefix_len: int
) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv6 network."""
    data = np.array([2, 16, *ipv6_network], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 16))
        ])
    )[0]
    mask = IPV6_MASK_LOOKUP_TABLE[prefix_len].to_bytes(16, 'big')
    addr, zone = compose(
        partial(ip_network, mask=mask, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert isinstance(addr, ip.IPv6Network)
    assert int(addr.network_address) == int.from_bytes(
        np.array(ipv6_network, dtype=np.uint8).tobytes(), byteorder='big'
    ) & IPV6_MASK_LOOKUP_TABLE[prefix_len]
    assert addr.prefixlen == prefix_len
    assert zone == -1


@hypothesis.given(
    ipv4_interface=st.lists(  # type: ignore
        st.integers(0, 255), max_size=4, min_size=4
    ),
    prefix_len=st.integers(0, 32)
)
def test_ipv4_ip_prefix_interface(
        ipv4_interface: List[int], prefix_len: int
) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv4 interface."""
    data = np.array([1, 4, *ipv4_interface], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 4))
        ])
    )[0]
    addr, zone = compose(
        partial(ip_interface, mask=prefix_len, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert isinstance(addr, ip.IPv4Interface)
    assert int(addr.ip) == int.from_bytes(
        np.array(ipv4_interface, dtype=np.uint8).tobytes(), byteorder='big'
    )
    assert addr.network.prefixlen == prefix_len
    assert zone == -1


@hypothesis.given(
    ipv4_interface=st.lists(  # type: ignore
        st.integers(0, 255), max_size=4, min_size=4
    ),
    prefix_len=st.integers(0, 32)
)
def test_ipv4_ip_mask_interface(
        ipv4_interface: List[int], prefix_len: int
) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv4 interface."""
    data = np.array([1, 4, *ipv4_interface], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 4))
        ])
    )[0]
    mask = IPV4_MASK_LOOKUP_TABLE[prefix_len].to_bytes(4, 'big')
    addr, zone = compose(
        partial(ip_interface, mask=mask, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert isinstance(addr, ip.IPv4Interface)
    assert int(addr.ip) == int.from_bytes(
        np.array(ipv4_interface, dtype=np.uint8).tobytes(), byteorder='big'
    )
    assert addr.network.prefixlen == prefix_len
    assert zone == -1


@hypothesis.given(
    ipv6_interface=st.lists(  # type: ignore
        st.integers(0, 255), max_size=16, min_size=16
    ),
    prefix_len=st.integers(0, 128)
)
def test_ipv6_ip_prefix_interface(
        ipv6_interface: List[int], prefix_len: int
) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv6 interface."""
    data = np.array([2, 16, *ipv6_interface], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 16))
        ])
    )[0]
    addr, zone = compose(
        partial(ip_interface, mask=prefix_len, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert isinstance(addr, ip.IPv6Interface)
    assert int(addr.ip) == int.from_bytes(
        np.array(ipv6_interface, dtype=np.uint8).tobytes(), byteorder='big'
    )
    assert addr.network.prefixlen == prefix_len
    assert zone == -1


@hypothesis.given(
    ipv6_interface=st.lists(  # type: ignore
        st.integers(0, 255), max_size=16, min_size=16
    ),
    prefix_len=st.integers(0, 128)
)
def test_ipv6_ip_mask_interface(
        ipv6_interface: List[int], prefix_len: int
) -> None:
    # pylint: disable=protected-access
    """Test converting bytes to an IPv6 interface."""
    data = np.array([2, 16, *ipv6_interface], dtype=np.uint64).view(
        np.dtype([
            ('inet_type', np.uint64), ('inet_len', np.uint64),
            ('inet_addr', (np.uint64, 16))
        ])
    )[0]
    mask = IPV6_MASK_LOOKUP_TABLE[prefix_len].to_bytes(16, 'big')
    addr, zone = compose(
        partial(ip_interface, mask=mask, zone=True),
        star(cast_ip_array),
        itemgetter('inet_addr', 'inet_len', 'inet_type')
    )(data)
    assert isinstance(addr, ip.IPv6Interface)
    assert int(addr.ip) == int.from_bytes(
        np.array(ipv6_interface, dtype=np.uint8).tobytes(), byteorder='big'
    )
    assert addr.network.prefixlen == prefix_len
    assert zone == -1
