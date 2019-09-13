"""Maybe functor, applicative, monad, and alternative types."""

from typing import Callable, Generic, Optional, Sequence, TypeVar

import attr

A = TypeVar('A')
B = TypeVar('B')


@attr.s(frozen=True, slots=True)
class Maybe(Generic[A]):
    """Maybe sum type."""

    def __attrs_post_init__(self) -> None:
        # pylint: disable=no-self-use
        """Disallow direct construction."""
        raise TypeError()

    def fmap(self, f: Callable[[A], B]) -> 'Maybe[B]':
        """Stub the functor fmap operator."""
        raise NotImplementedError()

    def apply(self, f: 'Maybe[Callable[[A], B]]') -> 'Maybe[B]':
        """Stub the applicative apply operator."""
        raise NotImplementedError()

    def bind(self, f: Callable[[A], 'Maybe[B]']) -> 'Maybe[B]':
        """Stub the monad bind operator."""
        raise NotImplementedError()

    def then(self, other: 'Maybe[B]') -> 'Maybe[B]':
        # pylint: disable=no-self-use
        """Implement the monad then operator."""
        return other

    def fail(self, e: Exception) -> A:
        """Stub the monad fail operator."""
        raise NotImplementedError()

    def choice(self, a: 'Maybe[A]') -> 'Maybe[A]':
        """Stub the alternative choice operator."""
        raise NotImplementedError()

    def from_maybe(self, a: A) -> A:
        """Stub from_maybe."""
        raise NotImplementedError()

    def to_optional(self) -> Optional[A]:
        """Stub to_optional."""
        raise NotImplementedError()

    @classmethod
    def from_optional(cls, a: 'Optional[A]') -> 'Maybe[A]':
        """Return a maybe from an optional."""
        if a is None:
            return Nothing()
        return Just(a)

    def combine(
            self, f: Callable[[A], Callable[[A], A]], other: 'Maybe[A]'
    ) -> 'Maybe[A]':
        """Combine maybes."""
        return (
            other.apply(self.fmap(f))
            .choice(self)
            .choice(other)
        )

    @classmethod
    def cat(cls, xs: 'Sequence[Maybe[A]]') -> Sequence[A]:
        """Return a sequence of all the Just values."""
        return [x.value for x in xs if isinstance(x, Just)]


@attr.s(frozen=True, slots=True)
class Just(Generic[A], Maybe[A]):
    """Just product type."""

    value: A = attr.ib()

    def __attrs_post_init__(self) -> None:
        # pylint: disable=no-self-use
        """Allow direct construction."""

    def fmap(self, f: Callable[[A], B]) -> 'Maybe[B]':
        """Implement the functor fmap operator."""
        return Just(f(self.value))

    def apply(self, f: 'Maybe[Callable[[A], B]]') -> 'Maybe[B]':
        """Implement the applicative apply operator."""
        if isinstance(f, Nothing):
            return Nothing()
        if isinstance(f, Just):
            return self.fmap(f.value)
        raise TypeError()

    def bind(self, f: Callable[[A], 'Maybe[B]']) -> 'Maybe[B]':
        """Implement the monad bind operator."""
        return f(self.value)

    def fail(self, _: Exception) -> A:
        """Implement the monad fail operator."""
        return self.value

    def choice(self, a: 'Maybe[A]') -> 'Maybe[A]':
        """Implement the alternative choice operator."""
        return Just(self.value)

    def from_maybe(self, _: A) -> A:
        """Unwrap a maybe."""
        return self.value

    def to_optional(self) -> Optional[A]:
        """Return a maybe from an optional."""
        return self.value


@attr.s(frozen=True, slots=True)
class Nothing(Generic[A], Maybe[A]):
    """Nothing product type."""

    def __attrs_post_init__(self) -> None:
        """Allow direct construction."""

    def fmap(self, _: Callable[[A], B]) -> 'Nothing[B]':
        # pylint: disable=no-self-use
        """Implement the functor fmap operator."""
        return Nothing()

    def apply(self, _: 'Maybe[Callable[[A], B]]') -> 'Maybe[B]':
        # pylint: disable=no-self-use
        """Implement the applicative apply operator."""
        return Nothing()

    def bind(self, _: Callable[[A], 'Maybe[B]']) -> 'Maybe[B]':
        # pylint: disable=no-self-use
        """Implement the monad bind operator."""
        return Nothing()

    def fail(self, e: Exception) -> A:
        """Implement the monad fail operator."""
        raise e

    def choice(self, a: 'Maybe[A]') -> 'Maybe[A]':
        """Implement the alternative choice operator."""
        return attr.evolve(a)

    def from_maybe(self, a: A) -> A:
        """Unwrap a maybe."""
        return a

    def to_optional(self) -> Optional[A]:
        """Return a maybe from an optional."""
        return None
