"""netframe::snmp::api::NullVarBind test cases."""

import pickle

import hypothesis
import hypothesis.strategies as st

from snmp_fetch.snmp.api import NullVarBind
from snmp_fetch.snmp.types import ObjectIdentity
from tests.snmp.strategies import oids


@hypothesis.given(
    oid=oids(),  # type: ignore
    oid_size=st.integers(min_value=0, max_value=(2 ** 32) - 1),
    value_size=st.integers(min_value=0, max_value=(2 ** 64) - 1)
)
def test_pickle_null_var_bind(
        oid: ObjectIdentity,
        oid_size: int,
        value_size: int,
) -> None:
    """Test pickling a NullVarBind."""
    var_bind = NullVarBind(
        oid,
        oid_size,
        value_size
    )
    assert var_bind == pickle.loads(pickle.dumps(var_bind))


@hypothesis.given(
    oid=oids(),  # type: ignore
    oid_size=st.integers(min_value=0, max_value=(2 ** 32) - 1),
    value_size=st.integers(min_value=0, max_value=(2 ** 64) - 1)
)
def test_null_var_bind_to_string(
        oid: ObjectIdentity,
        oid_size: int,
        value_size: int,
) -> None:
    """Test repr and str on a NullVarBind."""
    var_bind = NullVarBind(
        oid,
        oid_size,
        value_size
    )
    assert str(var_bind) == repr(var_bind)
    assert str(var_bind) == (
        f'NullVarBind('
        f'oid=\'.{".".join([str(i) for i in var_bind.oid])}\', '
        f'oid_size={oid_size}, '
        f'value_size={value_size})'
    )
