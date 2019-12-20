from typing import Callable, Sequence, Text, Tuple, TypeVar

import attr

from snmp_fetch.attoparsec import combinators

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
    return combinators.then(reserved(x), combinators.ret(f))


# addop :: Parser (Expr -> Expr -> Expr)
# addop = (infixOp "+" Add) <|> (infixOp "-" Sub)
def addop(s: Text) -> Sequence[Tuple[Callable[[Expr, Expr], Expr], Text]]:
    return combinators.option(infix_op('+', Add), infix_op('-', Sub))(s)


# mulop :: Parser (Expr -> Expr -> Expr)
# mulop = infixOp "*" Mul
def mulop(s: Text) -> Sequence[Tuple[Callable[[Expr, Expr], Expr], Text]]:
    return infix_op('*', Mul)(s)


# run :: String -> Expr
# run = runParser expr
def run(s: Text) -> Expr:
    return combinators.run_parser(expr, s)


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
