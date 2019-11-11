# pylint: disable=all
"""Stuff here."""

from typing import Any, Text, Generic, TypeVar, Type, Callable, cast, Union
from typing_extensions import Literal, Protocol


T = TypeVar('T')
object_identifier

class ObjectIdentifier(type):
    """Object type."""


class ObjectType(type):
    """Object type."""


V = TypeVar('V', bound=Callable[..., Any])


def oid(oid: Text) -> Callable[[T], T]:
    """Print stuff."""
    def wrapper(t: T) -> T:
        return t
    return wrapper


def object_type(oid: Text) -> T:
    """Do stuff."""
    class Stub:
        _oid: Text = oid
    return cast(T, Stub)


class Unsigned32(ObjectType):
    """asdf."""

    pass


class String(Generic[T], ObjectType):
    """Aasdf."""

    a: int

    pass


@oid('1.3.6.1.2.1')
class SnmpMib2(ObjectIdentifier):
    """SNMP MIB-B."""

    description = ot(dtype='S255')
    object_id = ot(dtype=ObjectIdentiferDtype())
    uptime = ot(dtype=
    contact: String
    name
    location
    services
    name: String[Literal[255]] = object_type('1')


print(Interface.__annotations__)
print(Interface.name)

