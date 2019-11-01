"""Enhanced IP address types.

Monkey patches the ipaddress module types to allow for IPv4 and IPv6 comparisons.
"""

import ipaddress as ip
from typing import TypeVar, Union

from snmp_fetch.utils import monkeypatch

T = TypeVar('T')


@monkeypatch(ip.IPv4Address, '__lt__')
def ipv4_address__lt__(self: T, other: T) -> bool:
    # pylint: disable=no-member
    """Compare less than on mixed IP address object types."""
    if isinstance(other, ip.IPv4Address):
        return ipv4_address__lt__.__lt__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Address):
        return True
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(ip.IPv4Address, '__le__')
def ipv4_address__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP address object types."""
    if isinstance(other, ip.IPv4Address):
        return ipv4_address__le__.__le__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Address):
        return True
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(ip.IPv4Address, '__gt__')
def ipv4_address__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP address object types."""
    if isinstance(other, ip.IPv4Address):
        return ipv4_address__gt__.__gt__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Address):
        return False
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(ip.IPv4Address, '__ge__')
def ipv4_address__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP address object types."""
    if isinstance(other, ip.IPv4Address):
        return ipv4_address__ge__.__ge__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Address):
        return False
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(ip.IPv6Address, '__lt__')
def ipv6_address__lt__(self: T, other: T) -> bool:
    """Compare less than on mixed IP address object types."""
    if isinstance(other, ip.IPv4Address):
        return False
    if isinstance(other, ip.IPv6Address):
        return ipv6_address__lt__.__lt__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(ip.IPv6Address, '__le__')
def ipv6_address__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP address object types."""
    if isinstance(other, ip.IPv4Address):
        return False
    if isinstance(other, ip.IPv6Address):
        return ipv6_address__le__.__le__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(ip.IPv6Address, '__gt__')
def ipv6_address__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP address object types."""
    if isinstance(other, ip.IPv4Address):
        return True
    if isinstance(other, ip.IPv6Address):
        return ipv6_address__gt__.__gt__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(ip.IPv6Address, '__ge__')
def ipv6_address__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP address object types."""
    if isinstance(other, ip.IPv4Address):
        return True
    if isinstance(other, ip.IPv6Address):
        return ipv6_address__ge__.__ge__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(ip.IPv4Network, '__lt__')
def ipv4_network__lt__(self: T, other: T) -> bool:
    """Compare less than on mixed IP network object types."""
    if isinstance(other, ip.IPv4Network):
        return ipv4_network__lt__.__lt__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Network):
        return True
    raise TypeError(f'{other} is not an IPv4Network or IPv6Network object')


@monkeypatch(ip.IPv4Network, '__le__')
def ipv4_network__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP network object types."""
    if isinstance(other, ip.IPv4Network):
        return ipv4_network__le__.__le__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Network):
        return True
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(ip.IPv4Network, '__gt__')
def ipv4_network__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP network object types."""
    if isinstance(other, ip.IPv4Network):
        return ipv4_network__gt__.__gt__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Network):
        return False
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(ip.IPv4Network, '__ge__')
def ipv4_network__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP network object types."""
    if isinstance(other, ip.IPv4Network):
        return ipv4_network__ge__.__ge__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Network):
        return False
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(ip.IPv6Network, '__lt__')
def ip6_network__lt__(self: T, other: T) -> bool:
    """Compare less than on mixed IP network object types."""
    if isinstance(other, ip.IPv4Network):
        return False
    if isinstance(other, ip.IPv6Network):
        return ip6_network__lt__.__lt__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(ip.IPv6Network, '__le__')
def ipv6_network__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP network object types."""
    if isinstance(other, ip.IPv4Network):
        return False
    if isinstance(other, ip.IPv6Network):
        return ipv6_network__le__.__le__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(ip.IPv6Network, '__gt__')
def ipv6_network__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP network object types."""
    if isinstance(other, ip.IPv4Network):
        return True
    if isinstance(other, ip.IPv6Network):
        return ipv6_network__gt__.__gt__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(ip.IPv6Network, '__ge__')
def ipv6_network__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP network object types."""
    if isinstance(other, ip.IPv4Network):
        return True
    if isinstance(other, ip.IPv6Network):
        return ipv6_network__ge__.__ge__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(ip.IPv4Interface, '__lt__')
def ipv4_interface__lt__(self: T, other: T) -> bool:
    """Compare less than on mixed IP interface object types."""
    if isinstance(other, ip.IPv4Interface):
        return ipv4_interface__lt__.__lt__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Interface):
        return True
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(ip.IPv4Interface, '__le__')
def ipv4_interface__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP interface object types."""
    if isinstance(other, ip.IPv4Interface):
        return ipv4_interface__le__.__le__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Interface):
        return True
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(ip.IPv4Interface, '__gt__')
def ipv4_interface__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP interface object types."""
    if isinstance(other, ip.IPv4Interface):
        return ipv4_interface__gt__.__gt__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Interface):
        return False
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(ip.IPv4Interface, '__ge__')
def ipv4_interface__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP interface object types."""
    if isinstance(other, ip.IPv4Interface):
        return ipv4_interface__ge__.__ge__(self, other)  # type: ignore
    if isinstance(other, ip.IPv6Interface):
        return False
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(ip.IPv6Interface, '__lt__')
def ipv6_interface__lt__(self: T, other: T) -> bool:
    """Compare less than on mixed IP interface object types."""
    if isinstance(other, ip.IPv4Interface):
        return False
    if isinstance(other, ip.IPv6Interface):
        return ipv6_interface__lt__.__lt__(self, other)  # type: ignore
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(ip.IPv6Interface, '__le__')
def ipv6_interface__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP interface object types."""
    if isinstance(other, ip.IPv4Interface):
        return False
    if isinstance(other, ip.IPv6Interface):
        return ipv6_interface__le__.__le__(self, other)  # type: ignore
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(ip.IPv6Interface, '__gt__')
def ipv6_interface__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP interface object types."""
    if isinstance(other, ip.IPv4Interface):
        return True
    if isinstance(other, ip.IPv6Interface):
        return ipv6_interface__gt__.__gt__(self, other)  # type: ignore
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(ip.IPv6Interface, '__ge__')
def ipv6_interface__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP interface object types."""
    if isinstance(other, ip.IPv4Interface):
        return True
    if isinstance(other, ip.IPv6Interface):
        return ipv6_interface__ge__.__ge__(self, other)  # type: ignore
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


IpAddress = Union[ip.IPv4Address, ip.IPv6Address]
IpNetwork = Union[ip.IPv4Network, ip.IPv6Network]
IpInterface = Union[ip.IPv4Interface, ip.IPv6Interface]

IPV4_PREFIX_LOOKUP_TABLE = {
    (0xFFFFFFFF << i) & 0xFFFFFFFF: 32 - i for i in range(0, 33)
}

IPV6_PREFIX_LOOKUP_TABLE = {
    (
        (0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF << i) &
        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    ): 128 - i
    for i in range(0, 129)
}


__all__ = [
    'ip'
]
