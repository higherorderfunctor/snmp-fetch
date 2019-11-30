"""netframe::snmp::api::Config test cases."""

import pickle

import hypothesis

from snmp_fetch.snmp.api import Config
from tests.snmp.strategies import configs


@hypothesis.given(
    config=configs()
)
def test_pickle_config(  # type: ignore
        config: Config
) -> None:
    """Test pickling an Config."""
    assert config == pickle.loads(pickle.dumps(config))


@hypothesis.given(
    config=configs()
)
def test_config_to_string(  # type: ignore
        config: Config
) -> None:
    """Test str and repr on an Config."""
    assert str(config) == repr(config)
    assert str(config) == (
        f'Config('
        f'retries={config.retries}, '
        f'timeout={config.timeout}, '
        f'var_binds_per_pdu={config.var_binds_per_pdu}, '
        f'bulk_repetitions={config.bulk_repetitions})'
    )
