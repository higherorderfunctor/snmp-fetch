# pylint: disable=invalid-name
"""String template."""

from typing import Any

import numpy as np

oid = (1, 3, 6, 1, 2, 1, 1, 5, 0)

var_bind = (oid, (len(oid) << 3, 255))

dtype = 'S256'


def validate(
        response: Any, osize: bool = True, vsize: bool = True
) -> None:
    """Validate no such instance response."""
    assert response['osize'] == len(oid)
    if osize:
        assert np.array_equal(
            response['oid'], np.array(oid)
        )
    assert response['type'] == 0x4
    assert response['vsize'] == 2
    if vsize:
        assert response['value'] == b'tt'
