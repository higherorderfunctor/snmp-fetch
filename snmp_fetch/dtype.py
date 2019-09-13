"""Datatype wrappers and helper functions."""

import ipaddress as ip
from operator import add
from typing import (
    Any, Callable, Optional, Sequence, Text, Tuple, TypeVar, Union
)

import numpy as np

from .fp import F as Fn
from .fp.either import Either, Left, Right
from .fp.maybe import Just, Maybe, Nothing
from .utils import align64

FuncType = Callable[..., Any]
F = TypeVar('F', bound=FuncType)
T = TypeVar('T')

DtypeStruct = Sequence[Tuple[Text, np.dtype]]


# monkey patch classes from the ipaddress module to support comparing IPv4 and
# IPv6 objects.

def monkeypatch(cls: type, method: Text) -> Callable[[F], F]:
    """Monkey patch and store base method on the function object."""
    def patch(f: F) -> F:
        if not getattr(cls, method) == f:
            setattr(f, method, getattr(cls, method))
            setattr(cls, method, f)
        return f
    return patch


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


def struct(ds: DtypeStruct) -> np.dtype:
    """Restructure a datatype."""
    return np.dtype(list(ds))


def destruct(ds: np.dtype) -> Either[Exception, DtypeStruct]:
    """Destructure a structured datatype."""
    if hasattr(ds, 'fields') and ds.fields:
        return Right([(f, d) for f, (d, *_) in ds.fields.items()])
    return Left(AttributeError(f'can only pad structured dtypes: {type(ds)}'))


def to_dtype(d: Optional[Union[np.dtype, DtypeStruct]]) -> Maybe[np.dtype]:
    """Convert varying forms of datatypes to a Maybe wrapped np.dtype."""
    if d is None:
        return Nothing()
    if isinstance(d, np.dtype):
        return Just(d)
    return Just(struct(d))


def concat(ds: Sequence[np.dtype]) -> Either[Exception, np.dtype]:
    """Concat structured datatypes."""
    def _concat(_ds: Sequence[np.dtype]) -> Either[Exception, DtypeStruct]:
        head, *tail = _ds
        if tail:
            return (
                destruct(head)
                .bind(lambda h: _concat(tail).fmap(Fn(add, h)))
            )
        return destruct(head)
    return (
        _concat(ds)
        .fmap(struct)
    )


def concatv(*ds: np.dtype) -> Either[Exception, np.dtype]:
    """Concat structured datatypes from a variable number of args."""
    return concat(ds)


def array(d: np.dtype, size: int) -> Maybe[np.dtype]:
    """Return an (n,) datatype if possible.

    Returns a bare datatype for a scalar request of Nothing with a negative
    size.
    """
    if size <= 0:
        return Nothing()
    if size == 1:
        return Just(d)
    return Just(np.dtype((d, size)))


def extend(ds: np.dtype, amount: int) -> np.dtype:
    """Extend the tail element of a structured datatype if possible.

    Currently only support character strings.
    """
    d = (
        destruct(ds)
        .fmap(lambda d: list(d[:-1]) + [(d[-1][0], extend(d[-1][1], amount))])
        .fmap(struct)
        .from_right(ds)
    )
    if d.kind == 'S':
        return np.dtype(f'S{d.itemsize + amount}')
    return d


def pad64(
        ds: np.dtype, label: Text = 'padding#'
) -> Either[Exception, np.dtype]:
    """Pad structured datatypes."""
    amount = align64(ds.itemsize) - ds.itemsize

    if amount == 0:
        return Right(ds)

    ds = extend(ds, amount)
    amount = align64(ds.itemsize) - ds.itemsize

    return (
        array(np.dtype(np.uint8), amount)
        .fmap(lambda d: concatv(ds, np.dtype([(label, d)])))
        .from_maybe(Right(ds))
    )


IPV4_PREFIX_LOOKUP_TABLE = {
    (0xFFFFFFFF << i) & 0xFFFFFFFF: 32 - i for i in range(0, 33)
}

IPV4_MASK_LOOKUP_TABLE = {
    v: k for k, v in IPV4_PREFIX_LOOKUP_TABLE.items()
}

IPV6_PREFIX_LOOKUP_TABLE = {
    (
        (0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF << i) &
        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    ): 128 - i
    for i in range(0, 129)
}

IPV6_MASK_LOOKUP_TABLE = {
    v: k for k, v in IPV6_PREFIX_LOOKUP_TABLE.items()
}


def ip_address(
        addr: bytes, zone: bool = False
) -> Union[IpAddress, Tuple[IpAddress, int]]:
    # pylint: disable=too-many-return-statements
    """Convert bytes to IP address."""
    if len(addr) == 4:
        if zone:
            return ip.IPv4Address(
                int.from_bytes(addr[:4], byteorder='big')
            ), -1
        return ip.IPv4Address(int.from_bytes(addr[:4], byteorder='big'))
    if len(addr) == 8:
        if zone:
            return (
                ip.IPv4Address(int.from_bytes(addr[:4], byteorder='big')),
                int.from_bytes(addr[-4:], byteorder='big')
            )
        return ip.IPv4Address(int.from_bytes(addr[:4], byteorder='big'))
    if len(addr) == 16:
        if zone:
            return ip.IPv6Address(
                int.from_bytes(addr[:16], byteorder='big')
            ), -1
        return ip.IPv6Address(int.from_bytes(addr[:16], byteorder='big'))
    if len(addr) == 20:
        if zone:
            return (
                ip.IPv6Address(int.from_bytes(addr[:16], byteorder='big')),
                int.from_bytes(addr[-4:], byteorder='big')
            )
        return ip.IPv6Address(int.from_bytes(addr[:16], byteorder='big'))
    raise TypeError(f'No matching address type for {addr}')


def ip_network(
        addr: bytes, mask: Union[bytes, int], zone: bool = False
) -> Union[IpNetwork, Tuple[IpNetwork, int]]:
    # pylint: disable=too-many-return-statements
    """Convert bytes to IP network."""
    if len(addr) == 4:
        if isinstance(mask, bytes):
            mask = IPV4_PREFIX_LOOKUP_TABLE[
                int.from_bytes(mask, byteorder='big')
            ]
        if zone:
            return ip.IPv4Network(
                (int.from_bytes(addr[:4], byteorder='big'), mask),
                strict=False
            ), -1
        return ip.IPv4Network(
            (int.from_bytes(addr[:4], byteorder='big'), mask), strict=False
        )
    if len(addr) == 8:
        if isinstance(mask, bytes):
            mask = IPV4_PREFIX_LOOKUP_TABLE[
                int.from_bytes(mask, byteorder='big')
            ]
        if zone:
            return ip.IPv4Network(
                (int.from_bytes(addr[:4], byteorder='big'), mask),
                strict=False
            ), int.from_bytes(addr[-4:], byteorder='big')
        return ip.IPv4Network(
            (int.from_bytes(addr[:4], byteorder='big'), mask), strict=False
        )
    if len(addr) == 16:
        if isinstance(mask, bytes):
            mask = IPV6_PREFIX_LOOKUP_TABLE[
                int.from_bytes(mask, byteorder='big')
            ]
        if zone:
            return ip.IPv6Network(
                (int.from_bytes(addr[:16], byteorder='big'), mask),
                strict=False
            ), -1
        return ip.IPv6Network(
            (int.from_bytes(addr[:16], byteorder='big'), mask), strict=False
        )
    if len(addr) == 20:
        if isinstance(mask, bytes):
            mask = IPV6_PREFIX_LOOKUP_TABLE[
                int.from_bytes(mask, byteorder='big')
            ]
        if zone:
            return ip.IPv6Network(
                (int.from_bytes(addr[:16], byteorder='big'), mask),
                strict=False
            ), int.from_bytes(addr[-4:], byteorder='big')
        return ip.IPv6Network(
            (int.from_bytes(addr[:16], byteorder='big'), mask), strict=False
        )
    raise TypeError(f'No matching network type for {addr}')


def ip_interface(
        addr: bytes, mask: Union[bytes, int], zone: bool = False
) -> Union[IpInterface, Tuple[IpInterface, int]]:
    # pylint: disable=too-many-return-statements
    """Convert bytes to IP interface."""
    if len(addr) == 4:
        if isinstance(mask, bytes):
            mask = IPV4_PREFIX_LOOKUP_TABLE[
                int.from_bytes(mask, byteorder='big')
            ]
        if zone:
            return ip.IPv4Interface(
                (int.from_bytes(addr[:4], byteorder='big'), mask)
            ), -1
        return ip.IPv4Interface(
            (int.from_bytes(addr[:4], byteorder='big'), mask)
        )
    if len(addr) == 8:
        if isinstance(mask, bytes):
            mask = IPV4_PREFIX_LOOKUP_TABLE[
                int.from_bytes(mask, byteorder='big')
            ]
        if zone:
            return ip.IPv4Interface(
                (int.from_bytes(addr[:4], byteorder='big'), mask)
            ), int.from_bytes(addr[-4:], byteorder='big')
        return ip.IPv4Interface(
            (int.from_bytes(addr[:4], byteorder='big'), mask)
        )
    if len(addr) == 16:
        if isinstance(mask, bytes):
            mask = IPV6_PREFIX_LOOKUP_TABLE[
                int.from_bytes(mask, byteorder='big')
            ]
        if zone:
            return ip.IPv6Interface(
                (int.from_bytes(addr[:16], byteorder='big'), mask)
            ), -1
        return ip.IPv6Interface(
            (int.from_bytes(addr[:16], byteorder='big'), mask)
        )
    if len(addr) == 20:
        if isinstance(mask, bytes):
            mask = IPV6_PREFIX_LOOKUP_TABLE[
                int.from_bytes(mask, byteorder='big')
            ]
        if zone:
            return ip.IPv6Interface(
                (int.from_bytes(addr[:16], byteorder='big'), mask)
            ), int.from_bytes(addr[-4:], byteorder='big')
        return ip.IPv6Interface(
            (int.from_bytes(addr[:16], byteorder='big'), mask)
        )
    raise TypeError(f'No matching interface type for {addr}')


def cast_ip_array(
        addr: np.ndarray, length: Optional[int] = None,
        ip_type: Optional[int] = None
) -> bytes:
    """Check IP types."""
    if length is None:
        length = len(addr)
    if ip_type is not None:
        if (ip_type, length) not in ((1, 4), (2, 16), (3, 8), (4, 20)):
            raise TypeError(
                f'No matching ip type for {(ip_type, length, addr)}'
            )
    return addr[:length].astype(np.uint8).tobytes()  # type: ignore
