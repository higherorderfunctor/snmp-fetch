# pylint: disable=ungrouped-imports  # fixed by #2824
"""Test suite for the C API."""

from typing import Sequence, Text, Tuple

import hypothesis
import hypothesis.strategies as st
import pytest

import snmp_fetch.capi as csnmp
import tests.strategies as _st
from snmp_fetch.utils import convert_oid
from snmp_fetch.var_bind import var_bind


@hypothesis.given(
    pdu_type=_st.pdu_type(),
    hosts=_st.valid_hostnames(),  # type: ignore
    oids=st.lists(st.one_of([
        st.just((1, 3, 6, 1, 2, 1, 1, 3)),
        st.just((1, 3, 6, 1, 2, 1, 1, 3, 0))
    ]), min_size=2)
)
@hypothesis.settings(
    deadline=None
)
def test_ambiguous_root_oids(
        pdu_type: csnmp.pdu_type,
        hosts: Sequence[Tuple[int, Text, Text]],
        oids: Sequence[Sequence[int]]
):
    """Test ambiguous root oids."""
    with pytest.raises(ValueError):
        vs = [
            var_bind(
                oid=convert_oid(oid)
            ) for oid in oids
        ]
        csnmp.fetch(
            pdu_type, hosts,
            [v() for v in vs]
        )
