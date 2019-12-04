"""Extended DataFrame functionality."""

from typing import Any, Tuple, Union

import numpy as np
import pandas as pd

from .utils import column_names


@pd.api.extensions.register_series_accessor('xt')
class ArrayExtractSeriesAccessor:
    # pylint: disable=too-few-public-methods
    """Inet Series accessor."""

    def __init__(self, obj: Any) -> None:
        """Initialize the pandas extension."""
        self.obj = obj

    # def __getattr__(self, name) -> Any:

    def __getitem__(self, ss: Union[int, slice, Tuple[Union[int, slice], ...]]) -> Any:
        """Slice the buffer."""
        if self.obj.empty:
            return self.obj
        arr = np.array(self.obj.values.tolist())
        if isinstance(ss, int):
            return pd.Series(arr[:, ss]).rename(self.obj.name)
        if isinstance(ss, slice):
            return pd.Series(tuple(arr[:, ss])).rename(self.obj.name)
        return pd.DataFrame(
            dict(zip(column_names(len(ss)), [
                arr[:, s] if isinstance(s, int) else tuple(arr[:, s]) for s in ss
            ])),
            index=self.obj.index
        )

    def implicit(self) -> Any:
        """Slice the buffer by a sized parameter."""
        return pd.DataFrame(
            self.obj.apply(lambda x: (x[1:int(x[0])+1], x[int(x[0])+1:])).tolist(),
            columns=list(column_names(2)),
            index=self.obj.index
        )
