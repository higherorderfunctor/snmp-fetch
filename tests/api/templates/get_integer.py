# pylint: disable=invalid-name
"""Integer template."""

from typing import Any

import numpy as np

oid = (1, 3, 6, 1, 2, 1, 2, 2, 1, 1, 1)

var_bind = (oid, (len(oid) << 3, 8))

dtype = np.uint64


def validate(
        response: Any, osize: bool = True, vsize: bool = True
) -> None:
    """Validate no such instance response."""
    assert response['osize'] == len(oid)
    if osize:
        assert np.array_equal(
            response['oid'], np.array(oid)
        )
    assert response['type'] == 0x2
    assert response['vsize'] == 8
    if vsize:
        assert response['value'] == 1
