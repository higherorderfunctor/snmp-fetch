"""netframe::snmp::api::Community test cases."""

import pickle

import hypothesis

from snmp_fetch.snmp.api import SnmpError
from snmp_fetch.snmp.utils import convert_oid
from tests.snmp.strategies import snmp_errors


@hypothesis.given(
    error=snmp_errors()  # type: ignore
)
def test_pickle_community(
        error: SnmpError
) -> None:
    """Test pickling an Community."""
    assert error == pickle.loads(pickle.dumps(error))


@hypothesis.given(
    error=snmp_errors()  # type: ignore
)
def test_community_to_string(
        error: SnmpError
) -> None:
    """Test str and repr on an SnmpCommunity."""
    assert str(error) == repr(error)
    assert str(error) == (
        f'SnmpError('
        f'type={str(error.type).split(".")[-1]}, '
        f'host={str(error.host)}, '
        f'sys_errno=' + (
            str(error.sys_errno) if error.sys_errno is not None else 'None'
        ) + ', '
        f'snmp_errno=' + (
            str(error.snmp_errno) if error.snmp_errno is not None else 'None'
        ) + ', '
        f'err_stat=' + (
            str(error.err_stat) if error.err_stat is not None else 'None'
        ) + ', '
        f'err_index=' + (
            str(error.err_index) if error.err_index is not None else 'None'
        ) + ', '
        f'err_oid=' + (
            "'"+convert_oid(error.err_oid)+"'" if error.err_oid is not None else 'None'
        ) + ', '
        f'message=' + (
            "'"+str(error.message)+"'" if error.message is not None else 'None'
        ) + ')'
    )
