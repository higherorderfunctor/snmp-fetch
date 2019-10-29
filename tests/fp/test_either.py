"""Either test cases."""

from typing import Any, Callable, Optional, Text, Type, TypeVar, Union

import hypothesis
import hypothesis.strategies as st
import pytest

from snmp_fetch.fp.either import Either, Left, Right

E = Exception

FuncType = Callable[..., Any]
F = TypeVar('F', bound=FuncType)


A = TypeVar('A')
B = TypeVar('B')


def exceptions(
        a: hypothesis.searchstrategy.strategies.SearchStrategy[A]
) -> hypothesis.searchstrategy.strategies.SearchStrategy[E]:
    """Generate Exceptions with supplied strategy."""
    return st.builds(Exception, a)


def lefts(
        a: hypothesis.searchstrategy.strategies.SearchStrategy[A]
) -> hypothesis.searchstrategy.strategies.SearchStrategy[Left[A, B]]:
    """Generate Lefts with supplied strategy."""
    return st.builds(Left, a)


def rights(
        b: hypothesis.searchstrategy.strategies.SearchStrategy[B]
) -> hypothesis.searchstrategy.strategies.SearchStrategy[Right[A, B]]:
    """Generate Rights with supplied strategy."""
    return st.builds(Right, b)


def eithers(
        a: hypothesis.searchstrategy.strategies.SearchStrategy[A],
        b: hypothesis.searchstrategy.strategies.SearchStrategy[B]
) -> hypothesis.searchstrategy.strategies.SearchStrategy[Either[A, B]]:
    """Generate Eithers with supplied strategies."""
    return st.one_of(lefts(a), rights(b))


@hypothesis.given(
    t=st.one_of(st.just(Either), st.just(Left), st.just(Right)),  # type: ignore
    v=st.one_of(st.integers(), st.floats(), st.text(), st.none())
)
def test_either(
        t: Type[Union[Either[Any, Any], Left[Any, Any], Right[Any, Any]]],
        v: Optional[Union[int, float, Text]]
) -> None:
    """Test Either construction."""
    if v is None:
        with pytest.raises(TypeError):
            t()  # type: ignore
    if t == Either:
        with pytest.raises(TypeError):
            t(v)  # type: ignore
    else:
        assert t(v).value is v  # type: ignore


@hypothesis.given(
    a=eithers(exceptions(st.text()), st.integers()),  # type: ignore
    f=st.functions(like=lambda x: None, returns=st.text())
)
def test_fmap(a: Either[E, int], f: Callable[[int], Text]) -> None:
    """Test fmap method."""
    if isinstance(a, Left):
        assert a.fmap(f) == a
    elif isinstance(a, Right):
        assert isinstance(a.fmap(f).value, Text)
    else:
        pytest.fail()


@hypothesis.given(
    a=eithers(exceptions(st.text()), st.integers()),  # type: ignore
    b=eithers(exceptions(st.text()), st.functions(
        like=lambda x: None, returns=st.text()
    ))
)
def test_apply(a: Either[E, int], b: Either[E, Callable[[int], Text]]) -> None:
    """Test apply method."""
    if isinstance(b, Left):
        assert a.apply(b) == b
    elif isinstance(b, Right):
        if isinstance(a, Left):
            assert a.apply(b) == a
        elif isinstance(b, Right):
            assert isinstance(a.apply(b).value, Text)
        else:
            pytest.fail()
    else:
        pytest.fail()


@hypothesis.given(
    a=eithers(exceptions(st.text()), st.integers()),  # type: ignore
    f=st.functions(
        like=lambda x: None, returns=eithers(exceptions(st.text()), st.text())
    )
)
def test_bind(a: Either[E, int], f: Callable[[int], Either[E, Text]]) -> None:
    """Test bind method."""
    if isinstance(a, Left):
        assert a.bind(f) == a
    elif isinstance(a, Right):
        bound = a.bind(f)
        if isinstance(bound, Left):
            assert isinstance(bound.value, Exception)
        elif isinstance(bound, Right):
            assert isinstance(bound.value, Text)
        else:
            pytest.fail()
    else:
        pytest.fail()


@hypothesis.given(
    a=eithers(exceptions(st.text()), st.integers()),  # type: ignore
    b=eithers(exceptions(st.text()), st.integers())
)
def test_then(a: Either[E, int], b: Either[E, int]) -> None:
    """Test then method."""
    assert a.then(b) == b


@hypothesis.given(
    e=eithers(st.text(), st.integers()),  # type: ignore
    a=st.text(),
    b=st.integers()
)
def test_from_left(e: Either[Text, int], a: Text, b: int) -> None:
    """Test from_left method."""
    if isinstance(e, Left):
        assert e.from_left(a) == e.value
    elif isinstance(e, Right):
        assert e.from_left(b) == b
    else:
        pytest.fail()


@hypothesis.given(
    e=eithers(st.text(), st.integers()),  # type: ignore
    a=st.text(),
    b=st.integers()
)
def test_from_right(e: Either[Text, int], a: Text, b: int) -> None:
    """Test from_right method."""
    if isinstance(e, Left):
        assert e.from_right(a) == a
    elif isinstance(e, Right):
        assert e.from_right(b) == e.value
    else:
        pytest.fail()


@hypothesis.given(
    e=eithers(st.one_of(exceptions(st.text()), st.text()), st.integers())  # type: ignore
)
def test_throw(e: Either[Union[Exception, Text], int]) -> None:
    """Test throw method."""
    if isinstance(e, Left):
        if isinstance(e.value, Exception):
            try:
                e.throw()
            # pylint: disable=broad-except
            except Exception as err:
                assert str(err) == str(e.value)
            else:
                pytest.fail()
        else:
            with pytest.raises(TypeError):
                e.throw()
    elif isinstance(e, Right):
        assert e.throw() == e.value
    else:
        pytest.fail()


@hypothesis.given(
    e=eithers(st.text(), st.integers()),  # type: ignore
)
def test_not_implemeneted(
        e: Either[Union[Exception, Text], int]
) -> None:
    """Test not implemented methods."""
    with pytest.raises(NotImplementedError):
        Either.fmap(e, lambda x: f'{x}')
    with pytest.raises(TypeError):
        e.apply(e, lambda x: f'{x}')  # type: ignore
    with pytest.raises(NotImplementedError):
        Either.bind(e, lambda x: Right(f'{x}'))
    with pytest.raises(NotImplementedError):
        Either.from_left(e, '')
    with pytest.raises(NotImplementedError):
        Either.from_right(e, 0)
    with pytest.raises(NotImplementedError):
        Either.throw(e)
