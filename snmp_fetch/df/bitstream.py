"""Helper functions for dealing with variable length data in a numpy array."""

from typing import Any, Callable, List, Optional, Text, Tuple, Type, Union

import numpy as np
from mypy_extensions import Arg, KwArg

EXTRACT_T = Callable[  # pylint: disable=invalid-name
    [Arg(Any, 'df'), Arg(Text, 'source'), KwArg(Any)], Tuple[Any, np.ndarray]
]
EXTRACT2_T = Callable[  # pylint: disable=invalid-name
    [Arg(Any, 'df'), Arg(Text, 'source'), KwArg(Any)], Tuple[Any, ...]
]
COLUMNS_T = Union[Text, List[Text]]  # pylint: disable=invalid-name
DTYPE_T = Union[Type[object], np.dtype]  # pylint: disable=invalid-name
DTYPES_T = Union[DTYPE_T, List[DTYPE_T]]  # pylint: disable=invalid-name
COMPOSABLE_T = Callable[[Text, Any], Tuple[Text, Any]]  # pylint: disable=invalid-name


def bitstream(source: Text, parsers: COMPOSABLE_T) -> Callable[[Any], Any]:
    """Extract values from a structured numpy array with variable length data."""
    def _bitstream(df: Any) -> Any:
        _, df = parsers(source, df)
        return df
    return _bitstream

# change compose to be fmap composition???
# with a discard attribute to break the chain if source == dest or source in dest


def parse(
        parser: EXTRACT_T,
        destination: COLUMNS_T,
        dtypes: Optional[DTYPES_T] = None,
        **kwargs: Any
) -> COMPOSABLE_T:
    """Extract one value from a structured numpy array with variable length data."""
    # flatten return type while enforcing strict input function that returns tail return type of an
    # numpy array
    def expand(f: EXTRACT2_T) -> EXTRACT2_T:
        def _expand(df: Any, source: Text, **kwargs: Any) -> Tuple[Any, ...]:
            results, remaining = f(df, source, **kwargs)
            if isinstance(results, tuple):
                return (*results, remaining)
            return results, remaining
        return _expand

    def _parse(source: Text, df: Any) -> Tuple[Text, Any]:
        # create columns even if DataFrame is empty
        if df.empty:
            if isinstance(destination, List) and isinstance(dtypes, List):
                for column, dtype in zip(destination, dtypes):
                    df[column] = None
                    df[column] = df[column].astype(dtype)  # TODO: handle optional
            else:
                df[destination] = None
                df[destination] = df[destination].astype(dtypes)  # TODO: handle optional
        else:
            columns = [*(destination if isinstance(destination, List) else [destination]), source]
            df[columns] = df.apply(
                expand(parser), axis=1, result_type='expand', source=source, **kwargs
            )
            if dtypes is not None:
                if isinstance(destination, List) and isinstance(dtypes, List):
                    for column, dtype in zip(destination, dtypes):
                        df[column] = df[column].astype(dtype)  # TODO: handle optional
                else:
                    df[destination] = df[destination].astype(dtypes)  # TODO: handle optional...
        return source, df
    return _parse


# Parsers
