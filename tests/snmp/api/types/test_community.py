"""netframe::snmp::api::Community test cases."""

import pickle

import hypothesis

from snmp_fetch.snmp.api import Community
from tests.snmp.strategies import communities


@hypothesis.given(
    community=communities()
)
def test_pickle_community(  # type: ignore
        community: Community
) -> None:
    """Test pickling an Community."""
    assert community == pickle.loads(pickle.dumps(community))


@hypothesis.given(
    community=communities()
)
def test_community_to_string(  # type: ignore
        community: Community
) -> None:
    """Test str and repr on an SnmpCommunity."""
    assert str(community) == repr(community)
    assert str(community) == (
        f'Community('
        f'version=v2c, '
        f'string=\'{community.string}\')'
    )
