"""Variable bindings."""

import inspect
import pprint
from collections import defaultdict
from functools import partial, reduce
from operator import attrgetter, methodcaller
from typing import Any, Callable, DefaultDict, Dict, Optional, Sequence, Text, Tuple, cast

import numpy as np
import pandas as pd
from toolz.functoolz import compose

from snmp_fetch.fp.maybe import Just, Maybe, Nothing
from snmp_fetch.utils import concatv_dtypes, dtype_array, dtype_fields
from .api import NullVarBind
from .utils import convert_oid, validate_oid

NULL_VAR_BIND_T = Tuple[Sequence[int], Tuple[int, int]]  # pylint: disable=invalid-name


class MetaObjectType(type):
    """Metaclass for ObjectTypes."""

    index: Optional[np.dtype] = None
    dtype: Optional[np.dtype] = None
    _parent: Maybe['MetaObjectType'] = Nothing()
    _children: Dict[Text, 'MetaObjectType']
    _oid: Maybe[Text] = Nothing()
    _hooks: DefaultDict[Text, Sequence[Callable[[Any], Any]]]

    def __init__(
            cls, class_name: Text, bases: Tuple[type, ...], attrs: Dict[Text, Any]
    ) -> None:
        """Initialize ObjectType."""
        super().__init__(class_name, bases, attrs)
        Maybe.from_optional(cls.index).fmap(dtype_fields).fmap(methodcaller('throw'))
        Maybe.from_optional(cls.dtype).fmap(dtype_fields).fmap(methodcaller('throw'))
        cls._parent.fmap(methodcaller('_append_child', cls))
        cls._children = {}
        cls._oid.fmap(validate_oid)
        valid_hooks = [
            'before_view',
            'after_view',
            'before_pivot',
            'before_merge',
            'after_merge'
        ]
        cls._hooks = defaultdict(list)
        for _, v in inspect.getmembers(cls, predicate=inspect.isfunction):
            _hook = getattr(v, '__hook__', None)
            if _hook is not None:
                if _hook not in valid_hooks:
                    raise ValueError(f"hook '{_hook}' is not a valid hook: {valid_hooks}")
                cls._hooks[_hook] = [v, *cls._hooks[_hook]]

    def _append_child(cls, child: 'MetaObjectType') -> None:
        """Append a child ObjectType to this ObjectType."""
        cls._children['.'.join([child.__module__, child.__qualname__])] = child

    _header_dtype = Just(np.dtype([
        ('#id', np.uint64),
        ('#community_index', np.uint64),
        ('#oid_size', np.uint64),
        ('#value_size', np.uint64),
        ('#value_type', np.uint64),
        ('#timestamp', 'datetime64[s]')
    ]))

    @property
    def _oid_dtype(cls) -> Maybe[np.dtype]:
        """Get the oid dtype."""
        return (
            cls._oid
            .fmap(convert_oid)
            .fmap(len)
            .bind(partial(dtype_array, np.dtype(np.uint64)))
            .fmap(lambda x: np.dtype([('#oid', x)]))
        )

    @property
    def _index(cls) -> Maybe[np.dtype]:
        # pylint: disable=no-member
        """Get the index dtype."""
        return Maybe.from_optional(cls.index)

    @property
    def _dtype(cls) -> Maybe[np.dtype]:
        """Get the value dtype."""
        return Maybe.from_optional(cls.dtype)

    @property
    def _matrix(cls) -> Sequence[Sequence['MetaObjectType']]:
        """Expand the tree of ObjectTypes into a matrix of ObjectTypes."""
        if not cls._children:
            return [[cls]]
        return [
            [cls, *col]
            for child in cls._children.values()
            for col in child._matrix  # pylint: disable=protected-access
        ]

    def null_var_binds(
            cls, param: Optional[Text] = None
    ) -> Sequence[NullVarBind]:
        """Get a description of null variable bindings to be filled."""
        def _check(null_var_bind: NULL_VAR_BIND_T) -> NULL_VAR_BIND_T:
            for size in null_var_bind[1]:
                if size % 8 != 0:
                    raise RuntimeError(f'dtype must be 64bit aligned: {null_var_bind}')
            return null_var_bind

        def _node_null_var_binds(_cls: MetaObjectType) -> NULL_VAR_BIND_T:
            # pylint: disable=protected-access, no-member  #1127
            return (
                _cls._oid.fmap(convert_oid).from_maybe([]),
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
            if cls._children:
                raise RuntimeError(
                    'ObjectType with a value dtype has children: '
                    f'cls={cls.__name__}: dtype={cls.dtype}: children={cls._children}'
                )
            return [
                NullVarBind(oid, oid_size, value_size)
                for oid, (oid_size, value_size)
                in [_check(_concat_null_var_binds(_node_null_var_binds(cls), param_null_var_bind))]
            ]

        matrix = cls._matrix

        index_set = {
            Maybe.reduce(concatv_dtypes, map(attrgetter('_index'), col))
            for col in matrix  # pylint: disable=not-an-iterable
        }

        if len(index_set) not in {0, 1}:
            raise RuntimeError(f'ObjectTypes do not share common index: {index_set}')

        _null_var_binds = [
            _check(reduce(
                _concat_null_var_binds,
                [*map(_node_null_var_binds, col), param_null_var_bind]
            ))
            for col in matrix  # pylint: disable=not-an-iterable
        ]

        return [
            NullVarBind(oid, oid_size, value_size)
            for oid, (oid_size, value_size) in _null_var_binds
        ]

    def _view(cls, arr: np.ndarray, col: Sequence['MetaObjectType']) -> Any:
        oid_dtype = (
            dtype_array(
                np.dtype(np.uint64),
                sum(map(len, Maybe.cat(map(
                    lambda x: x._oid.fmap(convert_oid), col  # pylint: disable=protected-access
                ))))
            )
            .fmap(lambda x: np.dtype([('#oid', x)]))
        )
        index_dtype = Maybe.reduce(concatv_dtypes, map(attrgetter('_index'), col))
        value_dtype = Maybe.reduce(concatv_dtypes, map(attrgetter('_dtype'), col))
        view_dtype = Maybe.reduce(
            concatv_dtypes, [cls._header_dtype, oid_dtype, index_dtype, value_dtype]
        )

        arr = reduce(lambda acc, var_bind: cast(
            np.ndarray,
            compose(*var_bind._hooks['before_view'])(acc)  # pylint: disable=protected-access
        ), col, arr)
        arr = view_dtype.fmap(arr.view).from_maybe(arr)  # type: ignore
        arr = reduce(lambda acc, var_bind: cast(
            np.ndarray,
            compose(*var_bind._hooks['after_view'])(acc)  # pylint: disable=protected-access
        ), col, arr)

        df = pd.DataFrame.from_records(
            arr.tolist(), columns=arr.dtype.names
        )

        # clean up dtypes of empty result
        if arr.size == 0:
            if isinstance(view_dtype, Just) and view_dtype.value.fields is not None:
                for column, dtype in view_dtype.value.fields.items():
                    try:
                        df[column] = df[column].astype(dtype[0])
                    except ValueError:
                        df[column] = df[column].astype(object)

        df = reduce(lambda acc, var_bind: (
            compose(*var_bind._hooks['before_pivot'])(acc)  # pylint: disable=protected-access
        ), col, df)

        if df.index.names is not None and [i for i in df.index.names if i is not None]:
            df = df.reset_index().set_index(['#id', *df.index.names])
        else:
            df = df.set_index('#id')

        return (
            df.drop(columns={
                '#community_index', '#oid_size', '#value_size', '#value_type', '#oid'
            }.intersection(df.columns))
        )

    @staticmethod
    def _pivot(a: Any, b: Any) -> Any:  # type: ignore
        """Pivot two ObjectType columns into a DataFrame."""
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
        matrix = cls._matrix
        df = reduce(cls._pivot, [cls._view(arr, col) for arr, col in zip(response, matrix)])
        df['#timestamp'] = df['#timestamp'].dt.tz_localize('UTC')
        df = df.reset_index().set_index('#id')
        df, data = reduce(
            lambda acc, var_bind: cast(
                Tuple[Any, Optional[Any]],
                compose(*var_bind._hooks['before_merge'])(acc)  # pylint: disable=protected-access
            ),
            [var_bind for col in matrix for var_bind in col],  # pylint: disable=not-an-iterable
            (df, data)
        )
        if data is not None:
            df = df.merge(data, how='outer', left_index=True, right_index=True)
        df = df.reset_index(drop=True)
        if index is not None:
            df = df.set_index(index)
        df = reduce(
            lambda acc, var_bind: (
                compose(*var_bind._hooks['after_merge'])(acc)  # pylint: disable=protected-access
            ),
            [var_bind for col in matrix for var_bind in col],  # pylint: disable=not-an-iterable
            df
        )
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
                    .fmap(lambda x: pp.pformat(dict(x.throw())).split('\n'))
                    .from_maybe([])
                )
                return '\n'.join(lines[:1] + [' ' * indent + line for line in lines[1:]])
            return (
                dtype.fmap(lambda x: [f'{label:{indent}s}{_dtype_description()}'])
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
                    cls._parent
                    .bind(lambda x: Maybe.from_optional(x.__name__))
                    .combine(lambda x: lambda y: ' '.join([x, y]), cls._oid)
                    .from_maybe('')
                ) + ' }'
            )

        def children_sequence_description() -> Sequence[Text]:
            if len(cls._children) > 1:
                return (
                    [f'\n{cls.__name__} ::= SEQUENCE {{'] +
                    [f'    {child.__name__}' for child in cls._children.values()] +
                    ['}']
                )
            return []

        def children_description() -> Sequence[Text]:
            return ['\n'+child.description for child in cls._children.values()]

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


class ObjectType(metaclass=MetaObjectType):
    # pylint: disable=too-few-public-methods
    """ObjectType definition."""

    def __attrs_post_init__(self) -> None:
        # pylint: disable=no-self-use
        """Raise error if type instance is created."""
        raise RuntimeError(
            'ObjectType is used for type level programming only; instances are not allowed'
        )
