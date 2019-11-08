"""Enhanced IP address types.

Monkey patches the ipaddress module types to allow for IPv4 and IPv6 comparisons.
"""

from ipaddress import (
    IPV4LENGTH, IPV6LENGTH, AddressValueError, IPv4Address, IPv4Interface, IPv4Network, IPv6Address,
    IPv6Interface, IPv6Network, NetmaskValueError, collapse_addresses, get_mixed_type_key,
    ip_address, ip_interface, ip_network, summarize_address_range, v4_int_to_packed,
    v6_int_to_packed
)
from typing import TypeVar, Union

from snmp_fetch.utils import monkeypatch

T = TypeVar('T')


@monkeypatch(IPv4Address, '__lt__')
def ipv4_address__lt__(self: T, other: T) -> bool:
    # pylint: disable=no-member
    """Compare less than on mixed IP address object types."""
    if isinstance(other, IPv4Address):
        return ipv4_address__lt__.__lt__(self, other)  # type: ignore
    if isinstance(other, IPv6Address):
        return True
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(IPv4Address, '__le__')
def ipv4_address__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP address object types."""
    if isinstance(other, IPv4Address):
        return ipv4_address__le__.__le__(self, other)  # type: ignore
    if isinstance(other, IPv6Address):
        return True
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(IPv4Address, '__gt__')
def ipv4_address__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP address object types."""
    if isinstance(other, IPv4Address):
        return ipv4_address__gt__.__gt__(self, other)  # type: ignore
    if isinstance(other, IPv6Address):
        return False
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(IPv4Address, '__ge__')
def ipv4_address__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP address object types."""
    if isinstance(other, IPv4Address):
        return ipv4_address__ge__.__ge__(self, other)  # type: ignore
    if isinstance(other, IPv6Address):
        return False
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(IPv6Address, '__lt__')
def ipv6_address__lt__(self: T, other: T) -> bool:
    """Compare less than on mixed IP address object types."""
    if isinstance(other, IPv4Address):
        return False
    if isinstance(other, IPv6Address):
        return ipv6_address__lt__.__lt__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(IPv6Address, '__le__')
def ipv6_address__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP address object types."""
    if isinstance(other, IPv4Address):
        return False
    if isinstance(other, IPv6Address):
        return ipv6_address__le__.__le__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(IPv6Address, '__gt__')
def ipv6_address__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP address object types."""
    if isinstance(other, IPv4Address):
        return True
    if isinstance(other, IPv6Address):
        return ipv6_address__gt__.__gt__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(IPv6Address, '__ge__')
def ipv6_address__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP address object types."""
    if isinstance(other, IPv4Address):
        return True
    if isinstance(other, IPv6Address):
        return ipv6_address__ge__.__ge__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Address or IPv6Address object')


@monkeypatch(IPv4Network, '__lt__')
def ipv4_network__lt__(self: T, other: T) -> bool:
    """Compare less than on mixed IP network object types."""
    if isinstance(other, IPv4Network):
        return ipv4_network__lt__.__lt__(self, other)  # type: ignore
    if isinstance(other, IPv6Network):
        return True
    raise TypeError(f'{other} is not an IPv4Network or IPv6Network object')


@monkeypatch(IPv4Network, '__le__')
def ipv4_network__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP network object types."""
    if isinstance(other, IPv4Network):
        return ipv4_network__le__.__le__(self, other)  # type: ignore
    if isinstance(other, IPv6Network):
        return True
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(IPv4Network, '__gt__')
def ipv4_network__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP network object types."""
    if isinstance(other, IPv4Network):
        return ipv4_network__gt__.__gt__(self, other)  # type: ignore
    if isinstance(other, IPv6Network):
        return False
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(IPv4Network, '__ge__')
def ipv4_network__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP network object types."""
    if isinstance(other, IPv4Network):
        return ipv4_network__ge__.__ge__(self, other)  # type: ignore
    if isinstance(other, IPv6Network):
        return False
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(IPv6Network, '__lt__')
def ip6_network__lt__(self: T, other: T) -> bool:
    """Compare less than on mixed IP network object types."""
    if isinstance(other, IPv4Network):
        return False
    if isinstance(other, IPv6Network):
        return ip6_network__lt__.__lt__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(IPv6Network, '__le__')
def ipv6_network__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP network object types."""
    if isinstance(other, IPv4Network):
        return False
    if isinstance(other, IPv6Network):
        return ipv6_network__le__.__le__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(IPv6Network, '__gt__')
def ipv6_network__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP network object types."""
    if isinstance(other, IPv4Network):
        return True
    if isinstance(other, IPv6Network):
        return ipv6_network__gt__.__gt__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(IPv6Network, '__ge__')
def ipv6_network__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP network object types."""
    if isinstance(other, IPv4Network):
        return True
    if isinstance(other, IPv6Network):
        return ipv6_network__ge__.__ge__(self, other)  # type: ignore
    raise TypeError(f'{other} is not an IPv4Network or IPv6network object')


@monkeypatch(IPv4Interface, '__lt__')
def ipv4_interface__lt__(self: T, other: T) -> bool:
    """Compare less than on mixed IP interface object types."""
    if isinstance(other, IPv4Interface):
        return ipv4_interface__lt__.__lt__(self, other)  # type: ignore
    if isinstance(other, IPv6Interface):
        return True
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(IPv4Interface, '__le__')
def ipv4_interface__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP interface object types."""
    if isinstance(other, IPv4Interface):
        return ipv4_interface__le__.__le__(self, other)  # type: ignore
    if isinstance(other, IPv6Interface):
        return True
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(IPv4Interface, '__gt__')
def ipv4_interface__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP interface object types."""
    if isinstance(other, IPv4Interface):
        return ipv4_interface__gt__.__gt__(self, other)  # type: ignore
    if isinstance(other, IPv6Interface):
        return False
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(IPv4Interface, '__ge__')
def ipv4_interface__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP interface object types."""
    if isinstance(other, IPv4Interface):
        return ipv4_interface__ge__.__ge__(self, other)  # type: ignore
    if isinstance(other, IPv6Interface):
        return False
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(IPv6Interface, '__lt__')
def ipv6_interface__lt__(self: T, other: T) -> bool:
    """Compare less than on mixed IP interface object types."""
    if isinstance(other, IPv4Interface):
        return False
    if isinstance(other, IPv6Interface):
        return ipv6_interface__lt__.__lt__(self, other)  # type: ignore
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(IPv6Interface, '__le__')
def ipv6_interface__le__(self: T, other: T) -> bool:
    """Compare less than or equal to on mixed IP interface object types."""
    if isinstance(other, IPv4Interface):
        return False
    if isinstance(other, IPv6Interface):
        return ipv6_interface__le__.__le__(self, other)  # type: ignore
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(IPv6Interface, '__gt__')
def ipv6_interface__gt__(self: T, other: T) -> bool:
    """Compare greater than on mixed IP interface object types."""
    if isinstance(other, IPv4Interface):
        return True
    if isinstance(other, IPv6Interface):
        return ipv6_interface__gt__.__gt__(self, other)  # type: ignore
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


@monkeypatch(IPv6Interface, '__ge__')
def ipv6_interface__ge__(self: T, other: T) -> bool:
    """Compare greater than or equal to on mixed IP interface object types."""
    if isinstance(other, IPv4Interface):
        return True
    if isinstance(other, IPv6Interface):
        return ipv6_interface__ge__.__ge__(self, other)  # type: ignore
    raise TypeError(
        f'{other} is not an IPv4Interface or IPv6interface object'
    )


IP_ADDRESS_T = Union[IPv4Address, IPv6Address]  # pylint: disable=invalid-name
IP_NETWORK_T = Union[IPv4Network, IPv6Network]  # pylint: disable=invalid-name
IP_INTERFACE_T = Union[IPv4Interface, IPv6Interface]  # pylint: disable=invalid-name

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
    'IP_ADDRESS_T',
    'IP_NETWORK_T',
    'IP_INTERFACE_T',
    'IPV4_PREFIX_LOOKUP_TABLE',
    'IPV6_PREFIX_LOOKUP_TABLE',
    'AddressValueError',
    'IPV4LENGTH',
    'IPV6LENGTH',
    'IPv4Address',
    'IPv4Interface',
    'IPv4Network',
    'IPv6Address',
    'IPv6Interface',
    'IPv6Network',
    'NetmaskValueError',
    'collapse_addresses',
    'get_mixed_type_key',
    'ip_address',
    'ip_interface',
    'ip_network',
    'summarize_address_range',
    'v4_int_to_packed',
    'v6_int_to_packed'
]
