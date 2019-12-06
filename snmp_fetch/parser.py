"""Numpy parser combinator."""

from typing import NewType, Generic, TypeVar, Callable, Sequence, Tuple

A = TypeVar('A')
B = TypeVar('B')

import numpy as np


Parser = Callable[[np.ndarray], Sequence[Tuple[A, np.ndarray]]]

def run_parser(parse: Parser[A], input: np.ndarray) -> A:
    [(res, rs)] = parse(input)
    return res

def item(input: np.ndarray) -> Sequence[Tuple[A, np.ndarray]]:
    return [(input[0], input[1:])]

# (a -> [b]) -> [a] -> [b]
def concat_map(f: Callable[[A], Sequence[B]], xs: Sequence[A]) -> Sequence[B]:
    return [
        y
        for x in xs
        for y in f(x)
    ]

# bind :: Parser a -> (a -> Parser b) -> Parser b
# bind p f = Parser $ \s -> concatMap (\(a, s') -> parse (f a) s') $ parse p s


def bind(parse: Parser[A], f: Callable[[A], Parser[B]]) -> Parser[B]:
    def map_f(a: A, _input: np.ndarray) -> Sequence[Tuple[B, np.ndarray]]:
        return f(a)(_input)
    return lambda input: concat_map(map_f, parse(input))
    

print(concat_map(range, [1, 2, 3]))

arr = np.array([0, 1, 2, 3])

print(item(arr))
