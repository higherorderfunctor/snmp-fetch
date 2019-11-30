"""netframe::snmp::api::ObjectIdentityParameter test cases."""

import pickle

import hypothesis

from snmp_fetch.snmp.api import ObjectIdentityParameter
from tests.snmp.strategies import object_identity_parameters


@hypothesis.given(
    parameter=object_identity_parameters()
)
def test_pickle_object_identity_parameter(  # type: ignore
        parameter: ObjectIdentityParameter
) -> None:
    """Test pickling an ObjectIdentityParameter."""
    assert parameter == pickle.loads(pickle.dumps(parameter))


@hypothesis.given(
    parameter=object_identity_parameters()
)
def test_object_identity_parameter_to_string(  # type: ignore
        parameter: ObjectIdentityParameter
) -> None:
    """Test repr and str on an ObjectIdentityParameter."""
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
