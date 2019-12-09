"""Semi-Typed Parser Combinator for numpy arrays.

Derived from https://github.com/sdiehl/write-you-a-haskell/blob/master/chapter3/parsec.hs
"""

from typing import Callable, Sequence, Text, Tuple, TypeVar

import attr

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


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
def satisfy(f: Callable[[Text], bool]) -> Parser[Text]:
    def _satisfy(c: Text) -> Parser[Text]:
        if f(c):
            return ret(c)
        return failure
    return bind(item, _satisfy)


####################################################################################################
# Combinators
####################################################################################################


# elem :: (Eq a) => a -> [a] -> Bool
def elem(x: Text, xs: Sequence[Text]) -> bool:
    return x == xs[0]


# flip :: (a -> b -> c) -> b -> a -> c
def flip(f: Callable[[A, B], C]) -> Callable[[B], Callable[[A], C]]:
    return lambda b: lambda a: f(a, b)


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
def is_digit(c: Text) -> bool:
    return c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']


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
        spaces,  # fix to allow spaces before op
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


# data Expr
#   = Add Expr Expr
#   | Mul Expr Expr
#   | Sub Expr Expr
#   | Lit Int
#   deriving Show
@attr.s(slots=True)
class Expr:
    pass


@attr.s(slots=True)
class _Add(Expr):
    a: Expr = attr.ib()
    b: Expr = attr.ib()


def Add(a: Expr, b: Expr) -> Expr:
    return _Add(a, b)


@attr.s(slots=True)
class _Mul(Expr):
    a: Expr = attr.ib()
    b: Expr = attr.ib()


def Mul(a: Expr, b: Expr) -> Expr:
    return _Mul(a, b)


@attr.s(slots=True)
class _Sub(Expr):
    a: Expr = attr.ib()
    b: Expr = attr.ib()


def Sub(a: Expr, b: Expr) -> Expr:
    return _Sub(a, b)


@attr.s(slots=True)
class Lit(Expr):
    n: int = attr.ib()


# eval :: Expr -> Int
# eval ex = case ex of
#   Add a b -> eval a + eval b
#   Mul a b -> eval a * eval b
#   Sub a b -> eval a - eval b
#   Lit  n
def eval(ex: Expr) -> int:
    if isinstance(ex, _Add):
        return eval(ex.a) + eval(ex.b)
    if isinstance(ex, _Mul):
        return eval(ex.a) * eval(ex.b)
    if isinstance(ex, _Sub):
        return eval(ex.a) - eval(ex.b)
    if isinstance(ex, Lit):
        return ex.n
    raise RuntimeError()


# int :: Parser Expr
# int = do
#   n <- number
#   return (Lit n)
def lit(s: Text) -> Sequence[Tuple[Expr, Text]]:
    return bind(number, lambda n: ret(Lit(n)))(s)


# expr :: Parser Expr
# expr = term `chainl1` addop
def expr(s: Text) -> Sequence[Tuple[Expr, Text]]:
    return chainl1(term, addop)(s)


# term :: Parser Expr
# term = factor `chainl1` mulop
def term(s: Text) -> Sequence[Tuple[Expr, Text]]:
    return chainl1(factor, mulop)(s)


# factor :: Parser Expr
# factor =
#       int
#   <|> parens expr
def factor(s: Text) -> Sequence[Tuple[Expr, Text]]:
    return option(lit, parens(expr))(s)


# infixOp :: String -> (a -> a -> a) -> Parser (a -> a -> a)
# infixOp x f = reserved x >> return f
def infix_op(x: Text, f: Callable[[A, A], A]) -> Parser[Callable[[A, A], A]]:
    return then(reserved(x), ret(f))


# addop :: Parser (Expr -> Expr -> Expr)
# addop = (infixOp "+" Add) <|> (infixOp "-" Sub)
def addop(s: Text) -> Sequence[Tuple[Callable[[Expr, Expr], Expr], Text]]:
    return option(infix_op('+', Add), infix_op('-', Sub))(s)


# mulop :: Parser (Expr -> Expr -> Expr)
# mulop = infixOp "*" Mul
def mulop(s: Text) -> Sequence[Tuple[Callable[[Expr, Expr], Expr], Text]]:
    return infix_op('*', Mul)(s)


# run :: String -> Expr
# run = runParser expr
def run(s: Text) -> Expr:
    return run_parser(expr, s)


# main :: IO ()
# main = forever $ do
#   putStr "> "
#     a <- getLine
#       print $ eval $ run a
if __name__ == "__main__":
    while True:
        try:
            print(eval(run(input('> '))))
        except Exception as err:
            print(err)
