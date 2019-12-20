# pylint: disable=all
# flake8: noqa
from typing import Generic, TypeVar, Sequence, Text, Any, Callable, Union, overload, Tuple, Type, Optional
from typing_extensions import Protocol, runtime_checkable

import numpy as np
import attr

# internal/types.py

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')

In = TypeVar('In', bound=np.ndarray)
R = TypeVar('R')
S = TypeVar('S')
T = TypeVar('T')



@attr.s(slots=True, frozen=True, auto_attribs=True)
class State(Generic[In]):
    pass




@attr.s(slots=True, frozen=True, auto_attribs=True)
class Pos:
    x: int
    def from_pos(self) -> int:
        return self.x


@attr.s(slots=True, frozen=True)
class IResult(Generic[In, R]):

    def fmap(self, f: Callable[[R], S]) -> 'IResult[In, S]':
        raise NotImplementedError()


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Fail(IResult[In, R]):
    i: In
    ctx: Sequence[Text]
    err: Text

    def fmap(self, _: Callable[[R], S]) -> IResult[In, S]:
        return Fail(self.i, self.ctx, self.err)


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Partial(IResult[In, R]):
    k: Callable[[In], IResult[In, R]]

    def fmap(self, f: Callable[[R], S]) -> IResult[In, S]:
        return Partial(lambda i: self.k(i).fmap(f))


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Done(IResult[In, R]):
    i: In
    result: R

    def fmap(self, f: Callable[[R], S]) -> IResult[In, S]:
        return Done(self.i, f(self.result))


@attr.s(slots=True, frozen=True)
class More:
    pass

@attr.s(slots=True, frozen=True)
class Complete(More):
    pass

@attr.s(slots=True, frozen=True)
class Incomplete(More):
    pass

Failure = Callable[[T, Pos, More, Sequence[Text], Text], IResult[In, R]]
Success = Callable[[T, Pos, More, A], IResult[In, R]]

Parser = Callable[[State[In], Pos, More, Failure[In, R], Success[In, R]], IResult[In, R]]

# https://www.schoolofhaskell.com/school/starting-with-haskell/libraries-and-frameworks/text-manipulation/attoparsec

