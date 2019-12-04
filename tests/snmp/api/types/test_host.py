"""netframe::snmp::api::Host test cases."""

import pickle

import hypothesis

from snmp_fetch.snmp.api import Host
from tests.snmp.strategies import hosts


@hypothesis.given(
    host=hosts()  # type: ignore
)
def test_pickle_host(
        host: Host
) -> None:
    """Test pickling a Host."""
    assert host == pickle.loads(pickle.dumps(host))


@hypothesis.given(
    host=hosts()  # type: ignore
)
def test_host_to_string(
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


@hypothesis.given(
    host=hosts()  # type: ignore
)
def test_host_snapshot(
        host: Host
) -> None:
    """Test repr and str on a Host."""
    snapshot = host.snapshot()
    assert str(snapshot) == (
        f'Host('
        f'id={host.id}, '
        f'hostname=\'{host.hostname}\', '
        f'communities={str(host.communities[:1])}, '
        f'parameters={str(host.parameters[:1]) if host.parameters else None}, '
        f'config={str(host.config)})'
    )
