"""
Port of nanoparsec in typed python from https://github.com/sdiehl/write-you-a-haskell/blob/master/chapter3/parsec.hs.
pip install attrs mypy
"""

from typing import Callable, Sequence, Text, Tuple, TypeVar

import attr

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


# concatMap :: (a -> [b]) -> [a] -> [b]
# Modified to support currying of 2-tuple
def concat_map(
        f: Callable[[A, C], Sequence[Tuple[B, C]]], xs: Sequence[Tuple[A, C]]
) -> Sequence[Tuple[B, C]]:
    return [
        y
        for x in xs
        for y in f(*x)
    ]


# newtype Parser a = Parser { parse :: String -> [(a,String)] }
Parser = Callable[[Text], Sequence[Tuple[A, Text]]]


# runParser :: Parser a -> String -> a
# runParser m s =
#   case parse m s of
#     [(res, [])] -> res
#     [(_, rs)]   -> error "Parser did not consume entire stream."
#     _           -> error "Parser error."
def run_parser(m: Parser[A], s: Text) -> A:
    try:
        [(res, rs)] = m(s)
        if not rs:
            return res
        raise ValueError(f'Parser did not consume entire stream: {res}: "{rs}"')
    except ValueError:
        raise ValueError('Parser error')


# item :: Parser Char
# item = Parser $ \s ->
#   case s of
#    []     -> []
#    (c:cs) -> [(c,cs)]
def item(s: Text) -> Sequence[Tuple[Text, Text]]:
    try:
        return [(s[0], s[1:])]
    except IndexError:
        return []


# (>>) :: Parser a -> Parser b -> Parser b
# k >> f = k >>= \_ -> f
def then(k: Parser[A], f: Parser[B]) -> Parser[B]:
    return bind(k, lambda _: f)


# bind :: Parser a -> (a -> Parser b) -> Parser b
# bind p f = Parser $ \s -> concatMap (\(a, s') -> parse (f a) s') $ parse p s
def bind(p: Parser[A], f: Callable[[A], Parser[B]]) -> Parser[B]:
    return lambda s: concat_map(lambda a, _s: f(a)(_s), p(s))


# unit :: a -> Parser a
# unit a = Parser (\s -> [(a,s)])
def ret(a: A) -> Parser[A]:
    return lambda s: [(a, s)]


# fmap :: (a -> b) -> Parser a -> Parser b
# fmap f (Parser cs) = Parser (\s -> [(f a, b) | (a, b) <- cs s])
def fmap(f: Callable[[A], B], cs: Parser[A]) -> Parser[B]:
    return lambda s: [
        (f(a), b) for (a, b) in cs(s)
    ]


# (<*>) :: Parser (a -> b) -> Parser a -> Parser b
# (Parser cs1) <*> (Parser cs2) = Parser (\s -> [(f a, s2) | (f, s1) <- cs1 s, (a, s2) <- cs2 s1])
def ap(cs1: Parser[Callable[[A], B]], cs2: Parser[A]) -> Parser[B]:
    return lambda s: [
        (f(a), s2)
        for (f, s1) in cs1(s)
        for (a, s2) in cs2(s1)
    ]


# combine :: Parser a -> Parser a -> Parser a
# combine p q = Parser (\s -> parse p s ++ parse q s)
def combine(p: Parser[A], q: Parser[A]) -> Parser[A]:
    return lambda s: [*p(s), *q(s)]


# failure :: Parser a
# failure = Parser (\cs -> [])
def failure(_: Text) -> Sequence[Tuple[A, Text]]:
    return []


# option :: Parser a -> Parser a -> Parser a
# option  p q = Parser $ \s ->
#   case parse p s of
#     []     -> parse q s
#     res    -> res
def option(p: Parser[A], q: Parser[A]) -> Parser[A]:
    def parser(s: Text) -> Sequence[Tuple[A, Text]]:
        res = p(s)
        return res if res else q(s)
    return parser


# -- | One or more.
# some :: f a -> f [a]
# some v = some_v
#   where
#     many_v = some_v <|> pure []
#     some_v = (:) <$> v <*> many_v
def some(v: Parser[A]) -> Parser[Sequence[A]]:
    def many_v(s: Text) -> Sequence[Tuple[Sequence[A], Text]]:
        return option(some_v, ret([]))(s)
    def some_v(s: Text) -> Sequence[Tuple[Sequence[A], Text]]:
        return ap(fmap(lambda x: lambda y: [x, *y], v), many_v)(s)
    return some_v


# -- | Zero or more.
# many :: f a -> f [a]
# many v = many_v
#   where
#     many_v = some_v <|> pure []
#     some_v = (:) <$> v <*> many_v
def many(v: Parser[A]) -> Parser[Sequence[A]]:
    def many_v(s: Text) -> Sequence[Tuple[Sequence[A], Text]]:
        return option(some_v, ret([]))(s)
    def some_v(s: Text) -> Sequence[Tuple[Sequence[A], Text]]:
        return ap(fmap(lambda x: lambda y: [x, *y], v), many_v)(s)
    return many_v


# satisfy :: (Char -> Bool) -> Parser Char
# satisfy p = item `bind` \c ->
#   if p c
#   then unit c
#   else failure
def satisfy(p: Callable[[Text], bool]) -> Parser[Text]:
    def _satisfy(c: Text) -> Parser[Text]:
        if p(c):
            return ret(c)
        return failure
    return bind(item, _satisfy)


####################################################################################################
# Combinators
####################################################################################################


# elem :: (Eq a) => a -> [a] -> Bool
# elem x = any (== x)
def elem(x: Text, xs: Sequence[Text]) -> bool:
    return x in xs


# flip :: (a -> b -> c) -> b -> a -> c
# flip f x y = f y x
def flip(f: Callable[[A, B], C]) -> Callable[[B], Callable[[A], C]]:
    return lambda x: lambda y: f(y, x)


# oneOf :: [Char] -> Parser Char
# oneOf s = satisfy (flip elem s)
def one_of(s: Sequence[Text]) -> Parser[Text]:
    return satisfy(flip(elem)(s))


# chainl :: Parser a -> Parser (a -> a -> a) -> a -> Parser a
# chainl p op a = (p `chainl1` op) <|> return a
def chainl(p: Parser[A], op: Parser[Callable[[A, A], A]], a: A) -> Parser[A]:
    return option(chainl1(p, op), ret(a))


# chainl1 :: Parser a -> Parser (a -> a -> a) -> Parser a
# p `chainl1` op = do {a <- p; rest a}
#   where rest a = (do f <- op
#                      b <- p
#                      rest (f a b))
#                  <|> return a
def chainl1(p: Parser[A], op: Parser[Callable[[A, A], A]]) -> Parser[A]:
    def rest(a: A) -> Parser[A]:
        def _rest(f: Callable[[A, A], A]) -> Parser[A]:
            return bind(p, lambda b: rest(f(a, b)))
        return option(bind(op, _rest), ret(a))
    return bind(p, rest)


# char :: Char -> Parser Char
# char c = satisfy (c ==)
def char(c: Text) -> Parser[Text]:
    return satisfy(lambda x: c == x)


# isDigit :: Char -> Bool
# isDigit c = (fromIntegral (ord c - ord '0') :: Word) <= 9
def is_digit(c: Text) -> bool:
    return 0 <= int(ord(c) - ord('0')) <= 9


# natural :: Parser Integer
# natural = read <$> some (satisfy isDigit)
def natural(s: Text) -> Sequence[Tuple[int, Text]]:
    return fmap(
        lambda ds: int(''.join(ds)),
        some(satisfy(is_digit))
    )(s)


# string :: String -> Parser String
# string [] = return []
# string (c:cs) = do { char c; string cs; return (c:cs)}
def string(s: Text) -> Parser[Text]:
    try:
        c, cs = s[0], s[1:]
        return then(then(char(c), string(cs)), ret(c+cs))
    except IndexError:
        return ret('')


# token :: Parser a -> Parser a
# token p = do { a <- p; spaces ; return a}
def token(p: Parser[A]) -> Parser[A]:
    return then(
        spaces,  # modified original to allow spaces before op
        bind(p, lambda a: then(spaces, ret(a)))
    )


# reserved :: String -> Parser String
# reserved s = token (string s)
def reserved(s: Text) -> Parser[Text]:
    return token(string(s))


# spaces :: Parser String
# spaces = many $ oneOf " \n\r"
def spaces(s: Text) -> Sequence[Tuple[Text, Text]]:
    return [
        (''.join(res), rs)
        for (res, rs) in many(one_of([' ', '\n', '\r']))(s)
    ]


# digit :: Parser Char
# digit = satisfy isDigit
def digit(s: Text) -> Sequence[Tuple[Text, Text]]:
    return satisfy(is_digit)(s)


# number :: Parser Int
# number = do
#   s <- string "-" <|> return []
#   cs <- some digit
#   return $ read (s ++ cs)
def number(s: Text) -> Sequence[Tuple[int, Text]]:
    return bind(
        option(string('-'), ret('')),
        lambda sign: bind(
            some(digit),
            lambda cs: ret(int(''.join([sign, *cs])))
        )
    )(s)


# parens :: Parser a -> Parser a
# parens m = do
#   reserved "("
#   n <- m
#   reserved ")"
#   return n
def parens(m: Parser[A]) -> Parser[A]:
    return then(reserved('('), bind(m, lambda n: then(reserved(')'), ret(n))))
