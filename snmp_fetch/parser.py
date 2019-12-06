# pylint: disable=all
# flake8: noqa
"""Semi-Typed Parser Combinator for numpy arrays.

Derived from https://github.com/sdiehl/write-you-a-haskell/blob/master/chapter3/parsec.hs
"""

from typing import Callable, Generic, Sequence, Tuple, TypeVar, Text, Optional, Union, cast

A = TypeVar('A')
B = TypeVar('B')
T = TypeVar('T')


def concat_map(
        f: Callable[[A, Sequence[T]], Sequence[Tuple[B, Sequence[T]]]],
        xs: Sequence[Tuple[A, Sequence[T]]]
) -> Sequence[Tuple[B, Sequence[T]]]:
    return [
        y
        for x in xs
        for y in f(*x)
    ]


Parser = Callable[[Sequence[T]], Sequence[Tuple[A, Sequence[T]]]]


def run_parser(m: Parser[T, A], s: Sequence[T]) -> Union[Optional[A], Tuple[A, Text]]:
    try:
        [(res, rs)] = m(s)
        if not rs:
            return res
        return res, 'Stream not fully consumed'
    except ValueError:
        return None


def item(s: Sequence[T]) -> Sequence[Tuple[T, Sequence[T]]]:
    return [(s[0], s[1:])]


def ret(a: A) -> Parser[T, A]:
    def parser(s: Sequence[T]) -> Sequence[Tuple[A, Sequence[T]]]:
        return [(a, s)]
    return parser


def fmap(f: Callable[[A], B], cs: Parser[T, A]) -> Parser[T, B]:
    def parser(s: Sequence[T]) -> Sequence[Tuple[B, Sequence[T]]]:
        return [
            (f(a), b) for (a, b) in cs(s)
        ]
    return parser


def apply(cs1: Parser[T, Callable[[A], B]], cs2: Parser[T, A]) -> Parser[T, B]:
    def parser(s: Sequence[T]) -> Sequence[Tuple[B, Sequence[T]]]:
        return [
            (f(a), s2)
            for (f, s1) in cs1(s)
            for (a, s2) in cs2(s1)
        ]
    return parser


def bind(p: Parser[T, A], f: Callable[[A], Parser[T, B]]) -> Parser[T, B]:
    def parser(s: Sequence[T]) -> Sequence[Tuple[B, Sequence[T]]]:
        return concat_map(lambda a, _s: f(a)(_s), p(s))
    return parser


def combine(p: Parser[T, A], q: Parser[T, A]) -> Parser[T, A]:
    def parser(s: Sequence[T]) -> Sequence[Tuple[A, Sequence[T]]]:
        return [*p(s), *q(s)]
    return parser


def failure(_: Sequence[T]) -> Sequence[Tuple[A, Sequence[T]]]:
    return []


def choice(p: Parser[T, A], q: Parser[T, A]) -> Parser[T, A]:
    def parser(s: Sequence[T]) -> Sequence[Tuple[A, Sequence[T]]]:
        res = p(s)
        if res:
            return res
        return q(s)
    return parser


def satisfy(f: Callable[[T], bool]) -> Parser[T, T]:
    def _satisfy(a: T) -> Parser[T, T]:
        if f(a):
            return ret(a)
        return failure
    return bind(item, _satisfy)


####################################################################################################
# Combinators
####################################################################################################


#def elem(x: A, xs: Sequence[A]) -> bool:
#    return x == xs[0]

def elem(x: Text, xs: Text) -> bool:
    return x == xs[0]


def flip(f: Callable[[A, B], T]) -> Callable[[B], Callable[[A], T]]:
    return lambda b: lambda a: f(a, b)


def one_of(s: Text) -> Parser[Text, Text]:
    return satisfy(flip(elem)(s))


def char(c: Text) -> Parser[Text, Text]:
    return satisfy(lambda x: x == c)


parser = choice(char('a'), char('b'))
x: Union[Optional[Text], Tuple[Text, Text]] = run_parser(
    parser, 'bbc'
)
print(x)
