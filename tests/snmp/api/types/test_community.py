"""netframe::snmp::api::Community test cases."""

import pickle
from typing import Text

import hypothesis
import hypothesis.strategies as st

from snmp_fetch.snmp.api import Community, Version


@hypothesis.given(
    index=st.integers(min_value=0, max_value=(2 ** 32) - 1),  # type: ignore
    version=st.just(Version.V2C),
    string=st.text()
)
def test_pickle_community(
        index: int,
        version: Version,
        string: Text
) -> None:
    """Test pickling an Community."""
    community = Community(
        index,
        version,
        string
    )
    assert community == pickle.loads(pickle.dumps(community))


@hypothesis.given(
    index=st.integers(min_value=0, max_value=(2 ** 32) - 1),  # type: ignore
    version=st.just(Version.V2C),
    string=st.text()
)
def test_community_to_string(
        index: int,
        version: Version,
        string: Text
) -> None:
    """Test str and repr on an SnmpCommunity."""
    community = Community(
        index,
        version,
        string
    )
    assert str(community) == repr(community)
    assert str(community) == (
        f'Community('
        f'index={index}, '
        f'version=v2c, '
        f'string=\'{string}\')'
    )
