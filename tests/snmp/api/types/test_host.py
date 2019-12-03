"""netframe::snmp::api::Host test cases."""

import pickle

import hypothesis

from snmp_fetch.snmp.api import Host
from tests.snmp.strategies import hosts


@hypothesis.given(
    host=hosts()
)
def test_pickle_host(  # type: ignore
        host: Host
) -> None:
    """Test pickling a Host."""
    assert host == pickle.loads(pickle.dumps(host))


@hypothesis.given(
    host=hosts()
)
def test_host_to_string(  # type: ignore
        host: Host
) -> None:
    """Test repr and str on a Host."""
    assert str(host) == repr(host)
    assert str(host) == (
        f'Host('
        f'id={host.id}, '
        f'hostname=\'{host.hostname}\', '
        f'communities={str(host.communities)}, '
        f'parameters={str(host.parameters) if host.parameters else None}, '
        f'config={str(host.config)})'
    )
