"""netframe::snmp::api::Config test cases."""

import pickle

import hypothesis
import hypothesis.strategies as st

from snmp_fetch.snmp.api import Config


@hypothesis.given(
    retries=st.integers(min_value=-1, max_value=(2 ** 32) - 1),  # type: ignore
    timeout=st.integers(min_value=-1, max_value=(2 ** 32) - 1),
    var_binds_per_pdu=st.integers(min_value=0, max_value=(2 ** 64) - 1),
    bulk_repetitions=st.integers(min_value=0, max_value=(2 ** 64) - 1),
)
def test_pickle_config(
        retries: int,
        timeout: int,
        var_binds_per_pdu: int,
        bulk_repetitions: int
) -> None:
    """Test pickling an Config."""
    config = Config(
        retries,
        timeout,
        var_binds_per_pdu,
        bulk_repetitions
    )
    assert config == pickle.loads(pickle.dumps(config))


@hypothesis.given(
    retries=st.integers(min_value=-1, max_value=(2 ** 32) - 1),  # type: ignore
    timeout=st.integers(min_value=-1, max_value=(2 ** 32) - 1),
    var_binds_per_pdu=st.integers(min_value=0, max_value=(2 ** 64) - 1),
    bulk_repetitions=st.integers(min_value=0, max_value=(2 ** 64) - 1),
)
def test_config_to_string(
        retries: int,
        timeout: int,
        var_binds_per_pdu: int,
        bulk_repetitions: int
) -> None:
    """Test str and repr on an Config."""
    config = Config(
        retries,
        timeout,
        var_binds_per_pdu,
        bulk_repetitions
    )
    assert str(config) == repr(config)
    assert str(config) == (
        f'Config('
        f'retries={retries}, '
        f'timeout={timeout}, '
        f'var_binds_per_pdu={var_binds_per_pdu}, '
        f'bulk_repetitions={bulk_repetitions})'
    )
