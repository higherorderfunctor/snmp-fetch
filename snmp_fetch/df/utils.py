"""Auxiliary helper functions for DataFrame processing."""

import numpy as np


def bytes_to_int(x: np.ndarray) -> int:
    """Convert bytes to a single integer."""
    return int.from_bytes(x.astype(np.uint8).tobytes(), byteorder='big')
