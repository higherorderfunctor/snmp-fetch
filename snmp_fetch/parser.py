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


def option(p: Parser[T, A], q: Parser[T, A]) -> Parser[T, A]:
    def parser(s: Sequence[T]) -> Sequence[Tuple[A, Sequence[T]]]:
        res = p(s)
        if res:
            return res
        return q(s)
    return parser


def some(v: Parser[T, A]) -> Parser[T, Sequence[A]]:
    def many_v(s: Sequence[T]) -> Sequence[Tuple[Sequence[A], Sequence[T]]]:
        return option(some_v, ret([]))(s)
    def some_v(s: Sequence[T]) -> Sequence[Tuple[Sequence[A], Sequence[T]]]:
        return apply(fmap(lambda x: lambda y: [x, *y], v), many_v)(s)
    return some_v


def many(v: Parser[T, A]) -> Parser[T, Sequence[A]]:
    def many_v(s: Sequence[T]) -> Sequence[Tuple[Sequence[A], Sequence[T]]]:
        return option(some_v, ret([]))(s)
    def some_v(s: Sequence[T]) -> Sequence[Tuple[Sequence[A], Sequence[T]]]:
        return apply(fmap(lambda x: lambda y: [x, *y], v), many_v)(s)
    return many_v


def satisfy(f: Callable[[T], bool]) -> Parser[T, T]:
    def _satisfy(c: T) -> Parser[T, T]:
        if f(c):
            return ret(c)
        return failure
    return bind(item, _satisfy)


####################################################################################################
# Combinators
####################################################################################################


def elem(x: T, xs: Sequence[T]) -> bool:
    return x == xs[0]


def flip(f: Callable[[A, B], T]) -> Callable[[B], Callable[[A], T]]:
    return lambda b: lambda a: f(a, b)


def one_of(s: Sequence[T]) -> Parser[T, T]:
    return satisfy(flip(elem)(s))

# chainl :: Parser a -> Parser (a -> a -> a) -> a -> Parser a
def chainl(p: Parser[T, A], op: Parser[T, Callable[[A, A], A]], a: A) -> Parser[T, A]:
    return option(chainl1(p, op), ret(a))

# chainl1 :: Parser a -> Parser (a -> a -> a) -> Parser a
def chainl1(p: Parser[T, A], op: Parser[T, Callable[[A, A], A]]) -> Parser[T, A]:
    def rest(a: A) -> Parser[T, A]:
        return option(bind(op, lambda f: bind(p, lambda b: rest(f(a, b)))), ret(a))
    return bind(p, lambda a: rest(a))


def char(c: Text) -> Parser[Text, Text]:
    return satisfy(lambda x: x == c)


def is_digit(d: Text) -> bool:
    return d in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']


def natural(s: Sequence[Text]) -> Sequence[Tuple[int, Sequence[Text]]]:
# def natural(s: Sequence[Text]) -> Parser[Text, int]:
    return fmap(
        lambda ds: int(''.join(ds)),
        some(satisfy(is_digit))
    )(s)


def then(k: Parser[T, A], f: Parser[T, B]) -> Parser[T, B]:
    return bind(k, lambda _: f)


def string(s: Sequence[Text]) -> Parser[Text, Text]:
    try:
        c, cs = s[0], s[1:]
        return then(then(char(c), string(cs)), ret(c+cs))
    except IndexError:
        return ret('')

s: Sequence[Text] = 'asdf'

parser = some(string('123'))
x = run_parser(
    parser, '1234bbbbbc'
)
print(x)

