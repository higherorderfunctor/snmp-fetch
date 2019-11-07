"""Variable bindings."""

import pprint
import re
from functools import partial, reduce
from operator import attrgetter, methodcaller
from typing import Any, Dict, Mapping, Optional, Sequence, Text, Tuple, Union, cast, overload

import attr
import numpy as np
import pandas as pd

from .fp.either import Either, Left, Right
from .fp.maybe import Just, Maybe, Nothing

DTYPE_FIELDS_T = (  # pylint: disable=invalid-name
    Mapping[str, Union[Tuple[np.dtype, int], Tuple[np.dtype, int, Any]]]
)
NULL_VAR_BIND_T = Tuple[Sequence[int], Tuple[int, int]]  # pylint: disable=invalid-name


@overload
def convert_oid(oid: Text) -> Sequence[int]:
    # pylint: disable=unused-argument
    # pragma: no cover
    """Convert a text oid to a sequence of integers."""
    ...  # pragma: no cover


@overload
def convert_oid(oid: Sequence[int]) -> Text:
    # pylint: disable=function-redefined, unused-argument
    # pragma: no cover
    """Convert a sequence of integers to a text oid."""
    ...  # pragma: no cover


def convert_oid(
        oid: Union[Text, Sequence[int]]
) -> Union[Sequence[int], Text]:
    # pylint: disable=function-redefined
    """Convert an oid between text and sequence of integers."""
    if isinstance(oid, Text):
        if re.match(r'^\.?\d+(\.\d+)*$', oid):
            if oid.startswith('.'):
                oid = oid[1:]
            return [int(x) for x in (oid).split('.')]
        raise ValueError(f'{oid} is not a valid oid')
    return '.'+'.'.join(map(str, oid))


@overload
def validate_oid(oid: Text) -> Text:
    # pylint: disable=unused-argument
    # pragma: no cover
    """Validate a text oid."""
    ...  # pragma: no cover


@overload
def validate_oid(oid: Sequence[int]) -> Sequence[int]:
    # pylint: disable=function-redefined, unused-argument
    """Validate a sequence of integers oid."""
    ...  # pragma: no cover


def validate_oid(
        oid: Union[Text, Sequence[int]]
) -> Union[Text, Sequence[int]]:
    """Validate an oid."""
    # pylint: disable=function-redefined
    return convert_oid(convert_oid(oid))


def dtype_fields(d: np.dtype) -> Either[Exception, DTYPE_FIELDS_T]:
    """Get structured dtype fields safely."""
    if d.fields is None:
        return Left(ValueError(f'structured dtype required: {d}'))
    return Right(d.fields)


def concat_dtypes(ds: Sequence[np.dtype]) -> np.dtype:
    """Concat structured datatypes."""
    def _concat(
            acc: Tuple[Mapping[Any, Any], int], a: np.dtype
    ) -> Tuple[DTYPE_FIELDS_T, int]:
        acc_fields, acc_itemsize = acc
        fields = dtype_fields(a).throw()
        intersection = set(acc_fields).intersection(set(fields))
        if intersection != set():
            raise ValueError(f'dtypes have overlapping fields: {intersection}')
        return (
            {
                **acc_fields,
                **{k: (d[0], d[1] + acc_itemsize) for k, d in fields.items()}
            },
            acc_itemsize + a.itemsize
        )
    # dtype.fields() doesn't match dtype constructor despite being compatible
    return np.dtype(reduce(_concat, ds, (cast(DTYPE_FIELDS_T, {}), 0))[0])  # type: ignore


def concatv_dtypes(*args: np.dtype) -> np.dtype:
    """Concat structured datatypes."""
    return concat_dtypes(args)


def dtype_array(d: Union[np.dtype, type], size: int) -> Maybe[np.dtype]:
    """Return an (n,) datatype if possible.

    Returns a bare datatype for a scalar request or Nothing with a negative size.
    """
    if size <= 0:
        return Nothing()
    if size == 1:
        if isinstance(d, np.dtype):
            return Just(d)
        return Just(np.dtype(d))
    return Just(np.dtype((d, size)))


class MetaVarBind(type):
    """Stuff."""

    parent: Optional['MetaVarBind'] = None
    oid: Optional[Text] = None
    index: Optional[np.dtype] = None
    dtype: Optional[np.dtype] = None
    _children: Maybe[Sequence['MetaVarBind']] = Nothing()

    def __init__(
            cls, class_name: Text, bases: Tuple[type, ...], attrs: Dict[Text, Any]
    ) -> None:
        """Perform basic checks of configured VarBind."""
        super().__init__(class_name, bases, attrs)
        if cls.oid is not None:
            cls.oid = validate_oid(cls.oid)
        Maybe.from_optional(cls.index).fmap(dtype_fields).fmap(methodcaller('throw'))
        Maybe.from_optional(cls.dtype).fmap(dtype_fields).fmap(methodcaller('throw'))
        Maybe.from_optional(cls.parent).fmap(methodcaller('_append_child', cls))

    def _append_child(cls, child: 'MetaVarBind') -> None:
        cls._children = (
            cls._children
            .choice(Just(cast(Sequence[MetaVarBind], list())))
            .fmap(lambda xs: [*xs, child])
        )

    _header_dtype = Just(np.dtype([
        ('#index', np.uint64),
        ('#oid_size', np.uint64),
        ('#result_size', np.uint64),
        ('#result_type', np.uint64),
        ('#timestamp', 'datetime64[s]'),
    ]))

    @property
    def _oid(cls) -> Maybe[Sequence[int]]:
        """Do some stuff."""
        return (
            Maybe.from_optional(cls.oid)
            .fmap(convert_oid)
        )

    @property
    def _oid_dtype(cls) -> Maybe[np.dtype]:
        # pylint: disable=no-member
        """Get the oid cstruct."""
        return (
            cls._oid
            .fmap(len)
            .bind(partial(dtype_array, np.dtype(np.uint64)))
            .fmap(lambda x: np.dtype([('#oid', x)]))
        )

    @property
    def _index(cls) -> Maybe[np.dtype]:
        # pylint: disable=no-member
        """Get the oid cstruct."""
        return Maybe.from_optional(cls.index)

    @property
    def _dtype(cls) -> Maybe[np.dtype]:
        """Get asdfasdf."""
        return Maybe.from_optional(cls.dtype)

    @property
    def _matrix(cls) -> Sequence[Sequence['MetaVarBind']]:
        if isinstance(cls._children, Nothing):
            return [[cls]]
        return [
            [cls, *col]
            for child in cls._children.from_maybe([])
            for col in child._matrix  # pylint: disable=protected-access
        ]

    def null_var_binds(
            cls, param: Optional[Text] = None
    ) -> Sequence[NULL_VAR_BIND_T]:
        """Return a null variable binding cstruct with optional parameter."""
        def _check(null_var_bind: NULL_VAR_BIND_T) -> NULL_VAR_BIND_T:
            for size in null_var_bind[1]:
                if size % 8 != 0:
                    raise RuntimeError(f'dtype must be 64bit aligned: {null_var_bind}')
            return null_var_bind

        def _node_null_var_binds(_cls: MetaVarBind) -> NULL_VAR_BIND_T:
            # pylint: disable=protected-access, no-member  #1127
            return (
                _cls._oid.from_maybe([]),
                (
                    _cls._oid_dtype.fmap(attrgetter('itemsize')).from_maybe(0) +
                    _cls._index.fmap(attrgetter('itemsize')).from_maybe(0),
                    _cls._dtype.fmap(attrgetter('itemsize')).from_maybe(0)
                )
            )

        def _concat_null_var_binds(a: NULL_VAR_BIND_T, b: NULL_VAR_BIND_T) -> NULL_VAR_BIND_T:
            return ([*a[0], *b[0]], (a[1][0] + b[1][0], a[1][1] + b[1][1]))

        param_null_var_bind = (
            Maybe.from_optional(param).fmap(convert_oid).from_maybe([]),
            (0, 0)
        )

        if cls.dtype is not None:
            if isinstance(cls._children, Just):
                raise RuntimeError(
                    'Variable binding with a dtype has children: '
                    f'cls={cls.__name__}: dtype={cls.dtype}: children={cls._children}'
                )
            return [_check(_concat_null_var_binds(_node_null_var_binds(cls), param_null_var_bind))]

        matrix = cls._matrix

        index_set = {
            reduce(concatv_dtypes, Maybe.cat(map(attrgetter('_index'), col)))
            for col in matrix  # pylint: disable=not-an-iterable
        }
        if len(index_set) != 1:
            raise RuntimeError(f'VarBinds do not share common index: {index_set}')

        return [
            _check(reduce(
                _concat_null_var_binds,
                [*map(_node_null_var_binds, col), param_null_var_bind]
            ))
            for col in matrix  # pylint: disable=not-an-iterable
        ]

    @staticmethod
    def before_view(arr: np.ndarray) -> np.ndarray:
        """Pre-process raw results from the C API."""
        return arr

    @staticmethod
    def after_view(arr: np.ndarray) -> np.ndarray:
        """Post-process results from the C API after the dtype view is applied."""
        return arr

    @staticmethod
    def before_pivot(df: Any) -> Any:  # type: ignore
        """Pre-process an indexed column."""
        return df

    @staticmethod
    def after_pivot(df: Any) -> Any:  # type: ignore
        """Post-process the indexed DataFrame after all columns have been jonined."""
        return df

    @staticmethod
    def before_merge(df: Any, original: Any) -> Tuple[Any, Any]:  # type: ignore
        """Pre-process the indexed DataFrame and original DataFrame before merging."""
        return df, original

    @staticmethod
    def after_merge(df: Any) -> Any:  # type: ignore
        """Post-process the final DataFrame."""
        return df

    def _view(cls, arr: np.ndarray, col: Sequence['MetaVarBind']) -> Any:
        oid_dtype = (
            dtype_array(
                np.dtype(np.uint64),
                sum(map(len, Maybe.cat(map(attrgetter('_oid'), col))))
            )
            .fmap(lambda x: np.dtype([('#oid', x)]))
        )
        index_dtype = Just(reduce(concatv_dtypes, Maybe.cat(map(attrgetter('_index'), col))))
        value_dtype = Just(reduce(concatv_dtypes, Maybe.cat(map(attrgetter('_dtype'), col))))

        view_dtype = concatv_dtypes(*Maybe.cat(
            [cls._header_dtype, oid_dtype, index_dtype, value_dtype]
        ))

        arr = reduce(lambda acc, var_bind: var_bind.before_view(acc), col, arr)
        arr = arr.view(view_dtype)
        arr = reduce(lambda acc, var_bind: var_bind.after_view(acc), col, arr)

        df = pd.DataFrame.from_records(
            arr.tolist(), columns=arr.dtype.names
            )

        # clean up dtypes of empty result
        if arr.size == 0:
            if view_dtype.fields is not None:
                for column, dtype in view_dtype.fields.items():
                    try:
                        df[column] = df[column].astype(dtype[0])
                    except ValueError:
                        df[column] = df[column].astype(object)

        df = reduce(lambda acc, var_bind: var_bind.before_pivot(acc), col, df)

        if df.index.names is not None and [i for i in df.index.names if i is not None]:
            df = df.reset_index().set_index(['#index', *df.index.names])
        else:
            df = df.set_index('#index')

        return (
            df.drop(columns={
                '#oid_size', '#result_size', '#result_type', '#oid'
            }.intersection(df.columns))
        )

    @staticmethod
    def _pivot(a: Any, b: Any) -> Any:  # type: ignore
        """Pivot the dataframe."""
        df = pd.merge(a, b, how='outer', left_index=True, right_index=True)
        df['#timestamp'] = (
            df[['#timestamp_x', '#timestamp_y']]
            .max(axis=1)
            .astype('datetime64[s]')
        )
        return df.drop(columns=['#timestamp_x', '#timestamp_y'])

    def to_pandas(
            cls, response: Sequence[np.ndarray], data: Optional[Any] = None,
            index: Optional[Sequence[Text]] = None
    ) -> Any:
        # pylint: disable=no-value-for-parameter
        """Reduce stuff."""
        df = reduce(cls._pivot, [cls._view(arr, col) for arr, col in zip(response, cls._matrix)])
        df['#timestamp'] = df['#timestamp'].dt.tz_localize('UTC')
        df = df.reset_index()
        if data is not None:
            df = (
                df.set_index('#index')
                .merge(data, how='outer', left_index=True, right_index=True)
                .reset_index()
            )
        df = df.drop(columns='#index')
        if index is not None:
            return df.set_index(index)
        return df

    @property
    def description(cls) -> Text:
        """Return string representation."""
        pp = pprint.PrettyPrinter(indent=4, width=60)

        def dtype_description(
                label: Text, dtype: Maybe[np.dtype], indent: int = 16
        ) -> Sequence[Text]:
            def _dtype_description() -> Sequence[Text]:
                lines = (
                    dtype.fmap(dtype_fields)
                    .fmap(lambda x: pp.pformat(dict(x.throw())))
                    .from_maybe(pp.pformat(dtype))
                    .split('\n')
                )
                return '\n'.join(lines[:1] + [' ' * indent + line for line in lines[1:]])
            return (
                Maybe.from_optional(cls.dtype)
                .fmap(lambda x: [f'{label:{indent}s}{_dtype_description()}'])
                .from_maybe([])
            )

        def var_bind_description() -> Sequence[Text]:
            return (
                Maybe.from_optional(cls.__doc__)
                .fmap(lambda x: ['DESCRIPTION'] + [
                    f'    {line}' for line in x.split('\n')
                ])
                .from_maybe([])
            )

        def parent_description() -> Text:
            return (
                '::= { ' + (
                    Maybe.from_optional(cls.parent)
                    .bind(lambda x: Maybe.from_optional(x.__name__))
                    .combine(lambda x: lambda y: ' '.join([x, y]), Maybe.from_optional(cls.oid))
                    .from_maybe('')
                ) + ' }'
            )

        def children_sequence_description() -> Sequence[Text]:
            return (
                cls._children
                .bind(lambda xs: Just(xs) if len(xs) > 1 else Nothing[Sequence[MetaVarBind]]())
                .fmap(lambda xs: (
                    [f'\n{cls.__name__} ::= SEQUENCE {{'] +
                    [f'    {x.__name__}' for x in xs] +
                    ['}']
                ))
                .from_maybe([])
            )

        def children_description() -> Sequence[Text]:
            return (
                cls._children
                .fmap(lambda xs: ['\n'+x.description for x in xs])
                .from_maybe([])
            )

        return '\n'.join([
            f'{cls.__name__} OBJECT-TYPE', *[
                f'    {line}' for line in [
                    *dtype_description('BASE_TYPE', cls._dtype),
                    *dtype_description('INDEX', cls._index),
                    *var_bind_description(),
                    parent_description()
                ]
            ],
            *children_sequence_description(),
            *children_description()
        ])

    def describe(cls) -> None:
        """Print the variable binding description."""
        print(cls.description)


@attr.s(frozen=True, slots=True)
class VarBind(metaclass=MetaVarBind):
    # pylint: disable=too-few-public-methods
    """Variable binding definition."""

    def __attrs_post_init__(self) -> None:
        # pylint: disable=no-self-use
        """Raise error if type instance is created."""
        raise RuntimeError(
            'VarBind is used for type level programming only; instances are not allowed'
        )
