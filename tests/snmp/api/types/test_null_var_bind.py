"""netframe::snmp::api::NullVarBind test cases."""

import pickle

import hypothesis

from snmp_fetch.snmp.api import NullVarBind
from tests.snmp.strategies import null_var_binds


@hypothesis.given(
    null_var_bind=null_var_binds()  # type: ignore
)
def test_pickle_null_var_bind(
        null_var_bind: NullVarBind
) -> None:
    """Test pickling a NullVarBind."""
    assert null_var_bind == pickle.loads(pickle.dumps(null_var_bind))


@hypothesis.given(
    null_var_bind=null_var_binds()  # type: ignore
)
def test_null_var_bind_to_string(
        null_var_bind: NullVarBind
) -> None:
    """Test repr and str on a NullVarBind."""
    assert str(null_var_bind) == repr(null_var_bind)
    assert str(null_var_bind) == (
        f'NullVarBind('
        f'oid=\'.{".".join([str(i) for i in null_var_bind.oid])}\', '
        f'oid_size={null_var_bind.oid_size}, '
        f'value_size={null_var_bind.value_size})'
    )
