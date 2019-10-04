"""SNMP config test cases."""

import pickle

import hypothesis
import hypothesis.strategies as st

from snmp_fetch import SnmpConfig


@hypothesis.given(
    retries=st.integers(min_value=-1, max_value=(2 ** 32) - 1),  # type: ignore
    timeout=st.integers(min_value=-1, max_value=(2 ** 32) - 1),
    max_active_sessions=st.integers(min_value=0, max_value=(2 ** 64) - 1),
    max_var_binds_per_pdu=st.integers(min_value=0, max_value=(2 ** 64) - 1),
    max_bulk_repetitions=st.integers(min_value=0, max_value=(2 ** 64) - 1),
)
def test_pickle_snmp_config(
        retries: int,
        timeout: int,
        max_active_sessions: int,
        max_var_binds_per_pdu: int,
        max_bulk_repetitions: int
) -> None:
    """Test pickling SNMP configs."""
    snmp_config = SnmpConfig(
        retries,
        timeout,
        max_active_sessions,
        max_var_binds_per_pdu,
        max_bulk_repetitions
    )
    assert snmp_config == pickle.loads(pickle.dumps(snmp_config))
