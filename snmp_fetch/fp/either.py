"""Maybe functor, applicative, and monad types."""

from typing import Callable, Generic, TypeVar

import attr

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


@attr.s(frozen=True, slots=True)
class Either(Generic[A, B]):
    """Either sum type."""

    def __attrs_post_init__(self) -> None:
        # pylint: disable=no-self-use
        """Disallow direct construction."""
        raise TypeError()

    def fmap(self, f: Callable[[B], C]) -> 'Either[A, C]':
        """Stub the functor fmap operator."""
        raise NotImplementedError()

    def apply(self, f: 'Either[A, Callable[[B], C]]') -> 'Either[A, C]':
        """Implement the applicative apply operator."""
        if isinstance(f, Left):
            return Left(f.value)
        if isinstance(f, Right):
            return self.fmap(f.value)
        raise TypeError()

    def bind(self, f: 'Callable[[B], Either[A, C]]') -> 'Either[A, C]':
        """Stub the monad bind operator."""
        raise NotImplementedError()

    def then(self, other: 'Either[A, C]') -> 'Either[A, C]':
        # pylint: disable=no-self-use
        """Implement the monad then operator."""
        return other

    def from_left(self, _: A) -> A:
        """Stub from_left."""
        raise NotImplementedError()

    def from_right(self, _: B) -> B:
        """Stub from_right."""
        raise NotImplementedError()

    def throw(self) -> B:
        """Stub throw."""
        raise NotImplementedError()


@attr.s(frozen=True, slots=True)
class Left(Generic[A, B], Either[A, B]):
    """Left product type."""

    value: A = attr.ib()

    def __attrs_post_init__(self) -> None:
        # pylint: disable=no-self-use
        """Allow direct construction."""

    def fmap(self, f: Callable[[B], C]) -> 'Either[A, C]':
        """Implement the functor fmap operator."""
        return Left(self.value)

    def bind(self, f: 'Callable[[B], Either[A, C]]') -> 'Either[A, C]':
        """Implement the monad bind operator."""
        return Left(self.value)

    def from_left(self, _: A) -> A:
        """Unwrap a left."""
        return self.value

    def from_right(self, b: B) -> B:
        """Return the default value."""
        return b

    def throw(self) -> B:
        # pylint: disable=raising-non-exception
        """Implement throw."""
        if isinstance(self.value, Exception):
            raise self.value
        raise TypeError(f'{self.value} is not an exception.')


@attr.s(frozen=True, slots=True)
class Right(Generic[A, B], Either[A, B]):
    """Right product type."""

    value: B = attr.ib()

    def __attrs_post_init__(self) -> None:
        """Allow construction."""

    def fmap(self, f: Callable[[B], C]) -> 'Either[A, C]':
        # pylint: disable=no-self-use
        """Implement the functor fmap operator."""
        return Right(f(self.value))

    def bind(self, f: 'Callable[[B], Either[A, C]]') -> 'Either[A, C]':
        """Implement the monad bind operator."""
        return f(self.value)

    def from_left(self, a: A) -> A:
        """Return the default value."""
        return a

    def from_right(self, _: B) -> B:
        """Unwrap a right."""
        return self.value

    def throw(self) -> B:
        """Unwrap a right."""
        return self.value
