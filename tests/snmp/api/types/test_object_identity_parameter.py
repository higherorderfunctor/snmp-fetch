"""netframe::snmp::api::ObjectIdentityParameter test cases."""

import pickle
from typing import Optional

import hypothesis
import hypothesis.strategies as st

from snmp_fetch.snmp.api import ObjectIdentityParameter
from snmp_fetch.snmp.types import ObjectIdentity
from tests.snmp.strategies import oids


@hypothesis.given(
    start=oids(),  # type: ignore
    end=st.one_of(st.none(), oids())
)
def test_pickle_object_identity_parameter(
        start: ObjectIdentity,
        end: Optional[ObjectIdentity]
) -> None:
    """Test pickling an ObjectIdentityParameter."""
    parameter = ObjectIdentityParameter(
        start,
        end
    )
    assert parameter == pickle.loads(pickle.dumps(parameter))


@hypothesis.given(
    start=oids(),  # type: ignore
    end=st.one_of(st.none(), oids())
)
def test_object_identity_parameter_to_string(
        start: ObjectIdentity,
        end: Optional[ObjectIdentity]
) -> None:
    """Test repr and str on an ObjectIdentityParameter."""
    parameter = ObjectIdentityParameter(
        start,
        end
    )
    assert str(parameter) == repr(parameter)
    assert str(parameter) == (
        f'ObjectIdentityParameter('
        f'start=\'.{".".join([str(i) for i in parameter.start])}\', '
        f'end='
        + (
            f'\'.{".".join([str(i) for i in parameter.end])}\''
            if parameter.end is not None else "None"
        ) +
        f")"
    )
